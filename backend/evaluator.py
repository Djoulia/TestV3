"""
Investment Criteria Evaluators
All evaluation functions for the 9 investment criteria
"""

import re
from typing import Dict
from config.settings import (
    EvaluationStatus, MIN_DIVIDEND_YIELD, MIN_INVESTMENT_SIZE, 
    PREFERRED_INVESTMENT_SIZE, MIN_TIMELINE_WEEKS, MIN_KGI_TIMELINE_WEEKS,
    MIN_IRR_THRESHOLD, TARGET_SECTORS, EXCLUDED_SECTORS, FUND_TYPES
)
from utils.helpers import (
    create_evaluation_result, check_keywords_present, check_all_keywords_present,
    extract_yield_percentage, extract_investment_amount, extract_timeline_weeks,
    extract_irr_percentage, format_currency, format_percentage
)

# =============================================================================
# CRITERION 1: GEOGRAPHY/STRUCTURE EVALUATOR
# =============================================================================

def evaluate_geography_structure(analysis_text: str) -> Dict[str, str]:
    """
    Evaluate Geography/Structure criterion
    
    Meets criteria if ANY of:
    1. GCC JV opportunity with expansion plans and partner structure
    2. Dividend-paying investment with yield > 4%
    3. KGI co-investment opportunity
    """
    
    # Check for GCC JV opportunity
    gcc_jv_found = _check_gcc_jv_opportunity(analysis_text)
    
    # Check for dividend-paying investment
    dividend_found = _check_dividend_opportunity(analysis_text)
    
    # Check for KGI co-investment
    kgi_found = _check_kgi_opportunity(analysis_text)
    
    # Determine result based on findings
    if gcc_jv_found:
        return create_evaluation_result(
            EvaluationStatus.MET,
            "GCC JV opportunity identified with expansion plans and partner structure"
        )
    elif dividend_found:
        return create_evaluation_result(
            EvaluationStatus.MET,
            f"Dividend-paying investment with yield greater than {MIN_DIVIDEND_YIELD}%"
        )
    elif kgi_found:
        return create_evaluation_result(
            EvaluationStatus.MET,
            "KGI co-investment opportunity identified"
        )
    else:
        return create_evaluation_result(
            EvaluationStatus.NOT_MET,
            f"Does not meet any of the three required categories: GCC JV, dividend-paying (>{MIN_DIVIDEND_YIELD}%), or KGI co-investment"
        )

def _check_gcc_jv_opportunity(analysis_text: str) -> bool:
    """Check for GCC Joint Venture opportunity"""
    gcc_present = check_keywords_present(analysis_text, ["gcc"])
    jv_present = check_keywords_present(analysis_text, ["joint venture", "jv"])
    expansion_indicators = check_keywords_present(analysis_text, ["expansion", "partner", "business model", "proven"])
    
    return gcc_present and jv_present and expansion_indicators

def _check_dividend_opportunity(analysis_text: str) -> bool:
    """Check for dividend-paying investment with sufficient yield"""
    dividend_present = check_keywords_present(analysis_text, ["dividend"])
    if not dividend_present:
        return False
    
    yield_percentage = extract_yield_percentage(analysis_text)
    return yield_percentage > MIN_DIVIDEND_YIELD

def _check_kgi_opportunity(analysis_text: str) -> bool:
    """Check for KGI co-investment opportunity"""
    kgi_present = check_keywords_present(analysis_text, ["kgi"])
    coinvestment_present = check_keywords_present(analysis_text, ["co-investment", "participation"])
    
    return kgi_present and coinvestment_present

# =============================================================================
# CRITERION 2: FINANCIAL MILESTONES EVALUATOR
# =============================================================================

def evaluate_financial_milestones(analysis_text: str) -> Dict[str, str]:
    """
    Evaluate Financial Milestones criterion
    
    Meets criteria if:
    1. New JV (not applicable), OR
    2. Already EBITDA positive, OR  
    3. Timeline to positive EBITDA within one year with current funding
    """
    
    # Check if it's a new JV
    is_new_jv = _check_new_jv(analysis_text)
    
    if is_new_jv:
        return create_evaluation_result(
            EvaluationStatus.MET,
            "Not applicable - New JV"
        )
    
    # Check EBITDA status
    ebitda_positive = _check_ebitda_positive(analysis_text)
    
    if ebitda_positive:
        return create_evaluation_result(
            EvaluationStatus.MET,
            "Company is already EBITDA positive"
        )
    
    # Check timeline and funding requirements
    timeline_within_year = _check_timeline_within_year(analysis_text)
    additional_funding_needed = _check_additional_funding_needed(analysis_text)
    
    if timeline_within_year and not additional_funding_needed:
        return create_evaluation_result(
            EvaluationStatus.MET,
            "Timeline to positive EBITDA is within one year with current funding"
        )
    else:
        return create_evaluation_result(
            EvaluationStatus.NOT_MET,
            "Timeline exceeds one year or additional funding rounds needed before profitability"
        )

def _check_new_jv(analysis_text: str) -> bool:
    """Check if this is a new joint venture"""
    new_present = check_keywords_present(analysis_text, ["new"])
    jv_present = check_keywords_present(analysis_text, ["joint venture", "jv"])
    return new_present and jv_present

def _check_ebitda_positive(analysis_text: str) -> bool:
    """Check if company is already EBITDA positive"""
    return check_keywords_present(analysis_text, ["ebitda positive", "positive ebitda"])

def _check_timeline_within_year(analysis_text: str) -> bool:
    """Check if timeline to profitability is within one year"""
    return check_keywords_present(analysis_text, [
        "within one year", 
        "12 months", 
        "less than a year"
    ])

def _check_additional_funding_needed(analysis_text: str) -> bool:
    """Check if additional funding rounds are needed"""
    return check_keywords_present(analysis_text, [
        "additional funding",
        "more funding", 
        "next round",
        "series"
    ])

# =============================================================================
# CRITERION 3: ASSET CLASS EXCLUSION EVALUATOR
# =============================================================================

def evaluate_asset_class_exclusion(analysis_text: str) -> Dict[str, str]:
    """
    Evaluate Asset Class Exclusion criterion
    
    Does NOT meet criteria if:
    - Fund investment (due to team bandwidth and 2025 objectives)
    
    Meets criteria if:
    - Direct company investment
    """
    
    # Check if it's a fund investment
    is_fund = _check_fund_investment(analysis_text)
    
    if is_fund:
        return create_evaluation_result(
            EvaluationStatus.NOT_MET,
            "Fund investment identified - excluded due to team bandwidth and 2025 objectives"
        )
    
    # Check if it's clearly a direct company investment
    is_direct = _check_direct_investment(analysis_text)
    
    if is_direct:
        return create_evaluation_result(
            EvaluationStatus.MET,
            "Direct company investment identified"
        )
    else:
        return create_evaluation_result(
            EvaluationStatus.NOT_MET,
            "Asset class information unclear or absent"
        )

def _check_fund_investment(analysis_text: str) -> bool:
    """Check if this is a fund investment"""
    return check_keywords_present(analysis_text, FUND_TYPES)

def _check_direct_investment(analysis_text: str) -> bool:
    """Check if this is a direct company investment"""
    return check_keywords_present(analysis_text, [
        "company",
        "business", 
        "startup",
        "direct investment"
    ])

# =============================================================================
# CRITERION 4: INVESTOR SYNDICATION EVALUATOR
# =============================================================================

def evaluate_investor_syndication(analysis_text: str) -> Dict[str, str]:
    """
    Evaluate Investor Syndication criterion
    
    Always meets criteria per Kanoo Ventures policy:
    - If lead investor identified: positive indicator
    - If no lead investor: not a rejection criterion
    """
    
    lead_investor_mentioned = _check_lead_investor(analysis_text)
    
    if lead_investor_mentioned:
        return create_evaluation_result(
            EvaluationStatus.MET,
            "Lead investor identified in syndicate"
        )
    else:
        return create_evaluation_result(
            EvaluationStatus.MET,
            "No lead investor identified - not a rejection criterion per Kanoo Ventures policy"
        )

def _check_lead_investor(analysis_text: str) -> bool:
    """Check if lead investor is mentioned"""
    return check_keywords_present(analysis_text, ["lead investor"])

# =============================================================================
# CRITERION 5: FEE TERMS EVALUATOR
# =============================================================================

def evaluate_fee_terms(analysis_text: str) -> Dict[str, str]:
    """
    Evaluate Fee Terms criterion
    
    Meets criteria if:
    - No direct management fees that would impact KV P&L
    
    Does NOT meet criteria if:
    - Management fees present that would hit KV P&L
    - Fee information not mentioned (missing info = red flag)
    """
    
    no_management_fees = _check_no_management_fees(analysis_text)
    management_fees_present = _check_management_fees_present(analysis_text)
    
    if no_management_fees:
        return create_evaluation_result(
            EvaluationStatus.MET,
            "No direct management fees that would impact KV P&L"
        )
    elif management_fees_present:
        return create_evaluation_result(
            EvaluationStatus.NOT_MET,
            "Management fees present that would hit KV P&L"
        )
    else:
        return create_evaluation_result(
            EvaluationStatus.NOT_MET,
            "Fee information not mentioned - missing information counts as red"
        )

def _check_no_management_fees(analysis_text: str) -> bool:
    """Check for explicit mention of no management fees"""
    return check_keywords_present(analysis_text, [
        "no management fee",
        "no direct management fee"
    ])

def _check_management_fees_present(analysis_text: str) -> bool:
    """Check for presence of management fees"""
    management_fee_present = check_keywords_present(analysis_text, ["management fee"])
    no_management_fee = _check_no_management_fees(analysis_text)
    
    return management_fee_present and not no_management_fee

# =============================================================================
# CRITERION 6: INVESTMENT SIZE EVALUATOR
# =============================================================================

def evaluate_investment_size(analysis_text: str) -> Dict[str, str]:
    """
    Evaluate Investment Size criterion
    
    Preferred: >= $7.9m (strong preference)
    Minimum: >= $5.0m 
    Below minimum: < $5.0m (portfolio management concerns)
    """
    
    investment_amount = extract_investment_amount(analysis_text)
    
    if investment_amount >= PREFERRED_INVESTMENT_SIZE:
        return create_evaluation_result(
            EvaluationStatus.MET,
            f"Investment size {format_currency(investment_amount)} meets preferred threshold with strong preference noted"
        )
    elif investment_amount >= MIN_INVESTMENT_SIZE:
        return create_evaluation_result(
            EvaluationStatus.MET,
            f"Investment size {format_currency(investment_amount)} meets minimum threshold with note about preference for larger tickets"
        )
    elif investment_amount > 0 and investment_amount < MIN_INVESTMENT_SIZE:
        return create_evaluation_result(
            EvaluationStatus.NOT_MET,
            f"Investment size {format_currency(investment_amount)} below ${MIN_INVESTMENT_SIZE}m minimum - portfolio management concerns about too many small deals"
        )
    else:
        return create_evaluation_result(
            EvaluationStatus.NOT_MET,
            "Investment size not specified"
        )

# =============================================================================
# CRITERION 7: PROCESS TIMELINE EVALUATOR
# =============================================================================

def evaluate_process_timeline(analysis_text: str) -> Dict[str, str]:
    """
    Evaluate Process Timeline criterion
    
    Meets criteria if:
    - KGI co-investment with >= 3 week timeline (lighter diligence)
    - Standard deal with >= 8 week timeline
    
    Does NOT meet if:
    - Timeline too short (risk of reduced diligence quality)
    - Timeline information absent
    """
    
    timeline_weeks = extract_timeline_weeks(analysis_text)
    is_kgi_coinvestment = _check_kgi_coinvestment(analysis_text)
    
    if is_kgi_coinvestment and timeline_weeks >= MIN_KGI_TIMELINE_WEEKS:
        return create_evaluation_result(
            EvaluationStatus.MET,
            f"KGI co-investment with {timeline_weeks} week timeline meets lighter diligence requirements"
        )
    elif timeline_weeks >= MIN_TIMELINE_WEEKS:
        return create_evaluation_result(
            EvaluationStatus.MET,
            f"Timeline of {timeline_weeks} weeks meets standard deal requirements"
        )
    elif timeline_weeks > 0:
        return create_evaluation_result(
            EvaluationStatus.NOT_MET,
            f"Timeline of {timeline_weeks} weeks too short - risk of reduced diligence quality"
        )
    else:
        return create_evaluation_result(
            EvaluationStatus.NOT_MET,
            "Timeline information absent"
        )

def _check_kgi_coinvestment(analysis_text: str) -> bool:
    """Check if this is a KGI co-investment"""
    kgi_present = check_keywords_present(analysis_text, ["kgi"])
    coinvestment_present = check_keywords_present(analysis_text, ["co-investment", "participation"])
    return kgi_present and coinvestment_present

# =============================================================================
# CRITERION 8: RETURN THRESHOLD EVALUATOR
# =============================================================================

def evaluate_return_threshold(analysis_text: str) -> Dict[str, str]:
    """
    Evaluate Return Threshold criterion
    
    Meets criteria if:
    - IRR >= 15%, OR
    - IRR < 15% but justified as low-risk opportunity
    
    Does NOT meet if:
    - IRR < 15% without low-risk justification
    - Return projections not provided
    """
    
    irr_percentage = extract_irr_percentage(analysis_text)
    low_risk_mentioned = _check_low_risk(analysis_text)
    
    if irr_percentage >= MIN_IRR_THRESHOLD:
        return create_evaluation_result(
            EvaluationStatus.MET,
            f"IRR of {format_percentage(irr_percentage)} meets {MIN_IRR_THRESHOLD}% threshold"
        )
    elif irr_percentage > 0 and irr_percentage < MIN_IRR_THRESHOLD and low_risk_mentioned:
        return create_evaluation_result(
            EvaluationStatus.MET,
            f"IRR of {format_percentage(irr_percentage)} below {MIN_IRR_THRESHOLD}% but justified as low-risk opportunity"
        )
    elif irr_percentage > 0 and irr_percentage < MIN_IRR_THRESHOLD:
        return create_evaluation_result(
            EvaluationStatus.NOT_MET,
            f"IRR of {format_percentage(irr_percentage)} below {MIN_IRR_THRESHOLD}% without low-risk justification"
        )
    else:
        return create_evaluation_result(
            EvaluationStatus.NOT_MET,
            "Return projections not provided"
        )

def _check_low_risk(analysis_text: str) -> bool:
    """Check if investment is characterized as low-risk"""
    return check_keywords_present(analysis_text, ["low risk", "low-risk"])

# =============================================================================
# CRITERION 9: SECTOR FOCUS EVALUATOR
# =============================================================================

def evaluate_sector_focus(analysis_text: str, met_criteria_count: int) -> Dict[str, str]:
    """
    Evaluate Sector Focus criterion
    
    Meets criteria if:
    - Company operates in target sectors (healthcare, education, data economy, energy transition, industrials)
    - Opportunistic consideration if meets other criteria and not in excluded sectors
    
    Does NOT meet if:
    - Company in consumer or traditional infrastructure sectors
    - Sector information not clear and insufficient other criteria met
    """
    
    # Check for target sectors
    sector_found = _find_target_sector(analysis_text)
    
    # Check for excluded sectors
    consumer_found = check_keywords_present(analysis_text, EXCLUDED_SECTORS)
    
    if sector_found:
        return create_evaluation_result(
            EvaluationStatus.MET,
            f"Company operates in {sector_found.title()} - target sector"
        )
    elif consumer_found:
        return create_evaluation_result(
            EvaluationStatus.NOT_MET,
            "Company in consumer or traditional infrastructure sectors"
        )
    else:
        # Check if meets other criteria for opportunistic consideration
        if met_criteria_count >= 6:  # Strong performance in other areas
            return create_evaluation_result(
                EvaluationStatus.MET,
                "Opportunistic - meets other criteria and not in excluded sectors"
            )
        else:
            return create_evaluation_result(
                EvaluationStatus.NOT_MET,
                "Sector information not clear"
            )

def _find_target_sector(analysis_text: str) -> str:
    """Find which target sector the company operates in"""
    for sector in TARGET_SECTORS:
        if sector in analysis_text.lower():
            return sector
    return ""