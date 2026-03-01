"""
Multi-Agent PRD Reviewer - Slack Bot
Coordinates Validator and Skeptic agents to provide comprehensive PRD reviews in Slack
"""

import os
import tempfile
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from flask import Flask, request
from dotenv import load_dotenv
from datetime import datetime

from agents.validator_agent import ValidatorAgent
from agents.skeptic_agent import SkepticAgent
from formatters.slack_formatter import format_review_for_slack

# Load environment variables
load_dotenv()

# Initialize Slack app
slack_app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

# Initialize Flask for deployment
flask_app = Flask(__name__)
handler = SlackRequestHandler(slack_app)

# Initialize agents
TEMPLATE_PATH = "templates/prd_template.yaml"
validator_agent = ValidatorAgent(TEMPLATE_PATH)
skeptic_agent = SkepticAgent()


@slack_app.command("/review-prd")
def handle_review_command(ack, command, client, logger):
    """
    Handle /review-prd slash command
    
    Flow:
    1. Acknowledge command immediately
    2. Extract PRD text and author
    3. Run both agents (Validator + Skeptic)
    4. Format results for Slack
    5. Post PERMANENT message to channel
    """
    
    # Acknowledge immediately (Slack requires < 3 seconds)
    ack()
    
    try:
        # Extract command details
        prd_text = command.get('text', '').strip()
        user_name = command.get('user_name', 'Unknown')
        channel_id = command.get('channel_id')
        
        # Validate PRD text provided
        if not prd_text:
            client.chat_postMessage(
                channel=channel_id,
                text="❌ Please provide PRD text after the command.\n\n*Usage:* `/review-prd [paste your PRD here]`"
            )
            return
        
        # Post "working on it" message
        working_msg = client.chat_postMessage(
            channel=channel_id,
            text=f"🤖 Analyzing PRD by @{user_name}...\n⏳ Running multi-agent review (this takes ~10 seconds)..."
        )
        
        # Extract PRD name from first line
        first_line = prd_text.split('\n')[0].strip()
        if first_line.startswith('#'):
            prd_name = first_line.lstrip('#').strip()
        else:
            prd_name = "Untitled PRD"
        
        # AGENT 1: Validator
        logger.info(f"Running Validator Agent for: {prd_name}")
        validation_results, score = validator_agent.validate(prd_text)
        validation_report = validator_agent.format_report(validation_results, score)
        
        # AGENT 2: Skeptical Tech Lead
        logger.info(f"Running Skeptic Agent for: {prd_name}")
        critique = skeptic_agent.challenge(prd_text, validation_report)
        
        # Compile review
        review = {
            "prd_name": prd_name,
            "timestamp": datetime.now().isoformat(),
            "author": user_name,
            "validation": validation_report,
            "technical_critique": critique['critique'],
            "summary": _generate_summary(validation_report, critique),
            "metadata": {
                "validator_score": score,
                "validator_status": validation_report['status'],
                "skeptic_tokens": critique['total_tokens'],
                "model_used": critique['model']
            }
        }
        
        # Format for Slack
        slack_message = format_review_for_slack(review)
        
        # Delete "working on it" message
        client.chat_delete(
            channel=channel_id,
            ts=working_msg['ts']
        )
        
        # Post final review (PERMANENT message)
        client.chat_postMessage(
            channel=channel_id,
            **slack_message,
            text=f"Multi-Agent PRD Review: {prd_name} by @{user_name}"  # Fallback text
        )
        
        logger.info(f"Review complete for: {prd_name} (Score: {score}/100)")
        
    except Exception as e:
        logger.error(f"Error in review: {str(e)}")
        client.chat_postMessage(
            channel=channel_id,
            text=f"❌ *Error processing review:*\n`{str(e)}`\n\nPlease contact the bot administrator."
        )


def _generate_summary(validation_report: dict, critique: dict) -> dict:
    """
    Generate executive summary from both agents
    
    Args:
        validation_report: Results from validator agent
        critique: Results from skeptic agent
        
    Returns:
        Dictionary with summary insights
    """
    score = validation_report['score']
    missing_critical = len(validation_report['missing_critical'])
    missing_high = len(validation_report['missing_high'])
    
    # Determine overall readiness
    if score >= 90 and missing_critical == 0:
        overall_status = "READY FOR ENGINEERING REVIEW"
        recommendation = "PRD meets quality standards. Address technical questions before kickoff."
    elif score >= 70:
        overall_status = "NEEDS ITERATION"
        recommendation = "Address missing sections and technical concerns before engineering review."
    else:
        overall_status = "NOT READY"
        recommendation = "Significant gaps require substantial work before engineering review."
    
    return {
        "overall_status": overall_status,
        "recommendation": recommendation,
        "completeness_score": score,
        "critical_gaps": missing_critical,
        "high_priority_gaps": missing_high
    }


@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    """
    Handle all Slack events
    Main endpoint that Slack sends commands to
    """
    return handler.handle(request)


@flask_app.route("/health", methods=["GET"])
def health_check():
    """
    Health check endpoint for monitoring
    """
    return {
        "status": "healthy",
        "service": "multi-agent-prd-reviewer-slack",
        "agents": ["validator", "skeptic_tech_lead"],
        "model": "claude-sonnet-4-20250514"
    }


if __name__ == "__main__":
    # For local development
    print("=" * 80)
    print("🚀 Multi-Agent PRD Reviewer Starting...")
    print("=" * 80)
    print(f"📋 Template: {TEMPLATE_PATH}")
    print(f"✅ Slack Bot Token: {os.environ.get('SLACK_BOT_TOKEN', 'NOT SET')[:20]}...")
    print(f"✅ Signing Secret: {'SET' if os.environ.get('SLACK_SIGNING_SECRET') else 'NOT SET'}")
    print(f"✅ Anthropic API Key: {'SET' if os.environ.get('ANTHROPIC_API_KEY') else 'NOT SET'}")
    print(f"🤖 Agents: Validator + Skeptical Tech Lead")
    print(f"🌐 Server will run on: http://localhost:3000")
    print(f"📡 Slack endpoint: http://localhost:3000/slack/events")
    print("=" * 80)
    flask_app.run(host="0.0.0.0", port=3000, debug=True)