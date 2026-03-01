"""
Formats multi-agent PRD review results for Slack
Uses Block Kit for rich, interactive messages
"""

def format_review_for_slack(review: dict) -> dict:
    """
    Convert multi-agent review into Slack Block Kit format
    
    Args:
        review: Review dictionary from orchestrator
        
    Returns:
        Dictionary with Slack blocks for rich message
    """
    
    prd_name = review.get('prd_name', 'Untitled PRD')
    summary = review['summary']
    validation = review['validation']
    critique = review['technical_critique']
    metadata = review['metadata']
    
    # Determine status emoji
    if summary['completeness_score'] >= 90:
        status_emoji = "✅"
    elif summary['completeness_score'] >= 70:
        status_emoji = "⚠️"
    else:
        status_emoji = "❌"
    
    # Build Slack blocks
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"📊 Multi-Agent PRD Review: {prd_name}"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Overall Status:* {summary['overall_status']} {status_emoji}\n*Recommendation:* {summary['recommendation']}"
            }
        },
        {
            "type": "divider"
        },
        # Validation Results Section
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*📋 VALIDATION RESULTS*\n\nScore: {validation['score']}/100 {validation['status_emoji']}\nStatus: {validation['status']}"
            }
        }
    ]
    
    # Add missing critical sections
    if validation['missing_critical']:
        critical_text = "*🔴 Critical Missing:*\n"
        for section in validation['missing_critical']:
            critical_text += f"• {section}\n"
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": critical_text
            }
        })
    
    # Add missing high priority sections
    if validation['missing_high']:
        high_text = "*🟡 High Priority Missing:*\n"
        for section in validation['missing_high']:
            high_text += f"• {section}\n"
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": high_text
            }
        })
    
    # Add found sections summary
    found_text = f"*✅ Found:* {validation['found_count']}/{validation['total_sections']} sections"
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": found_text
        }
    })
    
    blocks.append({"type": "divider"})
    
    # Technical Critique Section
    # Split critique into chunks (Slack has 3000 char limit per block)
    critique_chunks = _split_text(critique, 2900)
    
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "*🤔 TECHNICAL CRITIQUE*"
        }
    })
    
    for chunk in critique_chunks:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": chunk
            }
        })
    
    blocks.append({"type": "divider"})
    
    # Metadata footer
    blocks.append({
        "type": "context",
        "elements": [
            {
                "type": "mrkdwn",
                "text": f"🤖 Agents: Validator + Tech Lead | Model: {metadata['model_used']} | Tokens: {metadata['skeptic_tokens']}"
            }
        ]
    })
    
    return {"blocks": blocks}


def _split_text(text: str, max_length: int = 2900) -> list:
    """
    Split long text into chunks that fit Slack's block limits
    
    Args:
        text: Text to split
        max_length: Maximum characters per chunk
        
    Returns:
        List of text chunks
    """
    if len(text) <= max_length:
        return [text]
    
    chunks = []
    current_chunk = ""
    
    # Split by paragraphs to avoid breaking mid-sentence
    paragraphs = text.split('\n\n')
    
    for para in paragraphs:
        if len(current_chunk) + len(para) + 2 <= max_length:
            current_chunk += para + "\n\n"
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = para + "\n\n"
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks