"""
Utility functions for the Investment Screening System
"""

import re
from typing import List, Dict, Any, Optional
from config.settings import EvaluationStatus, STATUS_COLORS

def create_evaluation_result(status: str, explanation: str) -> Dict[str, str]:
    """Create a standardized evaluation result dictionary"""
    return {
        "status": status,
        "explanation": explanation,
        "color": STATUS_COLORS[status]
    }

def extract_company_name(analysis_text: str) -> str:
    """Extract company name from analysis text"""
    company_matches = re.search(r'company name[:\s]+([^\n\r\.]+)', analysis_text, re.IGNORECASE)
    if company_matches:
        return company_matches.group(1).strip()
    return "Unknown Company"

def extract_investment_amount(analysis_text: str) -> float:
    """Extract investment amount in millions from analysis text"""
    amount_matches = re.findall(r'\$(\d+(?:\.\d+)?)\s*m', analysis_text.lower())
    if amount_matches:
        return float(amount_matches[0])
    return 0.0

def extract_timeline_weeks(analysis_text: str) -> int:
    """Extract timeline in weeks from analysis text"""
    week_matches = re.findall(r'(\d+)\s*week', analysis_text.lower())
    if week_matches:
        return int(week_matches[0])
    return 0

def extract_irr_percentage(analysis_text: str) -> float:
    """Extract IRR percentage from analysis text"""
    irr_matches = re.findall(r'irr.*?(\d+(?:\.\d+)?)\s*%', analysis_text.lower())
    if irr_matches:
        return float(irr_matches[0])
    return 0.0

def extract_yield_percentage(analysis_text: str) -> float:
    """Extract dividend yield percentage from analysis text"""
    yield_matches = re.findall(r'(\d+(?:\.\d+)?)\s*%', analysis_text)
    for match in yield_matches:
        yield_val = float(match)
        if yield_val > 1:  # Assuming yields are typically single digit percentages
            return yield_val
    return 0.0

def check_keywords_present(analysis_text: str, keywords: List[str]) -> bool:
    """Check if any of the specified keywords are present in the analysis text"""
    text_lower = analysis_text.lower()
    return any(keyword.lower() in text_lower for keyword in keywords)

def check_all_keywords_present(analysis_text: str, keywords: List[str]) -> bool:
    """Check if all of the specified keywords are present in the analysis text"""
    text_lower = analysis_text.lower()
    return all(keyword.lower() in text_lower for keyword in keywords)

def count_met_criteria(criteria_evaluations: Dict[str, Dict[str, str]]) -> int:
    """Count how many criteria are marked as MET"""
    return sum(1 for criteria in criteria_evaluations.values() 
               if criteria["status"] == EvaluationStatus.MET)

def generate_overall_recommendation(met_count: int, total_count: int) -> str:
    """Generate overall recommendation based on criteria met"""
    if met_count >= 7:
        return "RECOMMEND for further due diligence"
    elif met_count >= 5:
        return "CONDITIONAL RECOMMEND - address key gaps"
    else:
        return "DO NOT RECOMMEND - insufficient criteria met"

def format_currency(amount: float) -> str:
    """Format currency amount for display"""
    if amount >= 1:
        return f"${amount}m"
    elif amount > 0:
        return f"${amount*1000}k"
    else:
        return "Not specified"

def format_percentage(percentage: float) -> str:
    """Format percentage for display"""
    if percentage > 0:
        return f"{percentage}%"
    else:
        return "Not specified"