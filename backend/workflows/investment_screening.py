"""
Investment Screening Workflow
Main orchestration of the investment screening process
"""

import json
import logging
from datetime import datetime
from typing import Dict, List

from config.settings import LIGHTON_API_KEY, LIGHTON_BASE_URL, MAX_DOCUMENTS_PER_BATCH
from clients.paradigm_client import ParadigmClient
from utils.helpers import (
    extract_company_name, count_met_criteria, 
    generate_overall_recommendation
)

# Import all evaluators from consolidated evaluator module
from evaluator import (
    evaluate_geography_structure,
    evaluate_financial_milestones,
    evaluate_asset_class_exclusion,
    evaluate_investor_syndication,
    evaluate_fee_terms,
    evaluate_investment_size,
    evaluate_process_timeline,
    evaluate_return_threshold,
    evaluate_sector_focus
)

logger = logging.getLogger(__name__)

# Initialize client
paradigm_client = ParadigmClient(LIGHTON_API_KEY, LIGHTON_BASE_URL)

async def execute_workflow(user_input: str) -> str:
    """Execute the complete investment screening workflow"""
    
    # STEP 1: Receive and identify the investment opportunity document
    attached_file_ids = globals().get('attached_file_ids', [])
    
    if not attached_file_ids:
        return "Error: No investment opportunity document provided. Please attach the document to analyze."
    
    logger.info(f"Processing {len(attached_file_ids)} attached files")
    
    # STEP 2: Search for and retrieve the investment opportunity document
    try:
        search_result = await _search_documents(attached_file_ids)
        documents = search_result.get("documents", [])
        
        if not documents:
            return "Error: Could not retrieve the investment opportunity document."
        
        document_ids = [str(doc["id"]) for doc in documents]
        logger.info(f"Found {len(document_ids)} documents for analysis")
        
    except Exception as e:
        logger.error(f"Document search failed: {str(e)}")
        return f"Error during document search: {str(e)}"
    
    # STEP 3: Analyze the investment opportunity document
    try:
        detailed_analysis = await _analyze_documents(document_ids)
        logger.info("Document analysis completed successfully")
        
    except Exception as e:
        logger.error(f"Document analysis failed: {str(e)}")
        return f"Error during document analysis: {str(e)}"
    
    # STEP 4-12: Evaluate all investment criteria
    try:
        criteria_evaluations = await _evaluate_all_criteria(detailed_analysis)
        logger.info("All criteria evaluated successfully")
        
    except Exception as e:
        logger.error(f"Criteria evaluation failed: {str(e)}")
        return f"Error during criteria evaluation: {str(e)}"
    
    # STEP 13: Generate comprehensive investment screening report
    try:
        final_report = await _generate_final_report(detailed_analysis, criteria_evaluations)
        logger.info("Final report generated successfully")
        return final_report
        
    except Exception as e:
        logger.error(f"Report generation failed: {str(e)}")
        return f"Error during report generation: {str(e)}"

async def _search_documents(attached_file_ids: List[int]) -> Dict:
    """Search for investment opportunity documents"""
    search_kwargs = {
        "query": "investment opportunity document type email pitch deck",
        "file_ids": attached_file_ids
    }
    return await paradigm_client.document_search(**search_kwargs)

async def _analyze_documents(document_ids: List[str]) -> str:
    """Analyze documents using the Paradigm client"""
    analysis_query = """Please provide a comprehensive analysis of this investment opportunity document. Extract the following key information:

1. Target company name and full legal entity structure
2. Detailed business model description including products/services offered
3. Geographic presence and expansion plans, specifically mentioning any GCC region intentions
4. Financial information including current EBITDA status, runway to profitability, funding requirements, and dividend policy if mentioned
5. Investment terms including proposed ticket size, management fees structure, and timeline expectations
6. Sector classification and sub-sector details
7. Return projections including IRR if provided
8. Investor syndicate composition including lead investor status
9. Partnership or joint venture structures if applicable
10. Any mentions of KGI involvement or co-investment opportunities

Please be thorough and specific in your analysis, noting when information is not available."""
    
    if len(document_ids) > MAX_DOCUMENTS_PER_BATCH:
        # Process in batches
        analysis_results = []
        for i in range(0, len(document_ids), MAX_DOCUMENTS_PER_BATCH):
            batch = document_ids[i:i+MAX_DOCUMENTS_PER_BATCH]
            result = await paradigm_client.analyze_documents_with_polling(analysis_query, batch)
            analysis_results.append(result)
        return "\n\n".join(analysis_results)
    else:
        return await paradigm_client.analyze_documents_with_polling(analysis_query, document_ids)

async def _evaluate_all_criteria(detailed_analysis: str) -> Dict[str, Dict[str, str]]:
    """Evaluate all investment criteria"""
    criteria_evaluations = {}
    
    # Evaluate each criterion
    criteria_evaluations["Geography/Structure"] = evaluate_geography_structure(detailed_analysis)
    criteria_evaluations["Financial Milestones"] = evaluate_financial_milestones(detailed_analysis)
    criteria_evaluations["Asset Class Exclusion"] = evaluate_asset_class_exclusion(detailed_analysis)
    criteria_evaluations["Investor Syndication"] = evaluate_investor_syndication(detailed_analysis)
    criteria_evaluations["Fee Terms"] = evaluate_fee_terms(detailed_analysis)
    criteria_evaluations["Investment Size"] = evaluate_investment_size(detailed_analysis)
    criteria_evaluations["Process Timeline"] = evaluate_process_timeline(detailed_analysis)
    criteria_evaluations["Return Threshold"] = evaluate_return_threshold(detailed_analysis)
    
    # Sector evaluation needs met criteria count for opportunistic consideration
    met_count = count_met_criteria(criteria_evaluations)
    criteria_evaluations["Sector Focus"] = evaluate_sector_focus(detailed_analysis, met_count)
    
    return criteria_evaluations

async def _generate_final_report(detailed_analysis: str, criteria_evaluations: Dict[str, Dict[str, str]]) -> str:
    """Generate the final investment screening report"""
    current_date = datetime.now().strftime("%B %d, %Y")
    company_name = extract_company_name(detailed_analysis)
    
    # Count met vs not met criteria
    met_count = count_met_criteria(criteria_evaluations)
    total_count = len(criteria_evaluations)
    
    # Generate overall recommendation
    overall_recommendation = generate_overall_recommendation(met_count, total_count)
    
    report_prompt = f"""Generate a comprehensive investment screening report with the following information:

COMPANY: {company_name}
DATE: {current_date}
ANALYSIS: {detailed_analysis}
CRITERIA RESULTS: {json.dumps(criteria_evaluations, indent=2)}
MET CRITERIA: {met_count}/{total_count}
RECOMMENDATION: {overall_recommendation}

Format the report exactly as follows:

# INVESTMENT OPPORTUNITY SCREENING REPORT
**Date:** {current_date}

## {company_name}

### Executive Summary
[Provide 3-5 sentence overview of the opportunity including business model, investment size, and key highlights]

### Detailed Opportunity Summary
[Provide comprehensive business description, market opportunity, team background if available, and unique value proposition]

### Investment Criteria Evaluation

| Criterion | Evaluation |
|-----------|------------|
| {criteria_evaluations["Geography/Structure"]["color"]} Geography/Structure | {criteria_evaluations["Geography/Structure"]["explanation"]} |
| {criteria_evaluations["Financial Milestones"]["color"]} Financial Milestones | {criteria_evaluations["Financial Milestones"]["explanation"]} |
| {criteria_evaluations["Asset Class Exclusion"]["color"]} Asset Class Exclusion | {criteria_evaluations["Asset Class Exclusion"]["explanation"]} |
| {criteria_evaluations["Investor Syndication"]["color"]} Investor Syndication | {criteria_evaluations["Investor Syndication"]["explanation"]} |
| {criteria_evaluations["Fee Terms"]["color"]} Fee Terms | {criteria_evaluations["Fee Terms"]["explanation"]} |
| {criteria_evaluations["Investment Size"]["color"]} Investment Size | {criteria_evaluations["Investment Size"]["explanation"]} |
| {criteria_evaluations["Process Timeline"]["color"]} Process Timeline | {criteria_evaluations["Process Timeline"]["explanation"]} |
| {criteria_evaluations["Return Threshold"]["color"]} Return Threshold | {criteria_evaluations["Return Threshold"]["explanation"]} |
| {criteria_evaluations["Sector Focus"]["color"]} Sector Focus | {criteria_evaluations["Sector Focus"]["explanation"]} |

### Overall Recommendation
{overall_recommendation}

**Criteria Met:** {met_count} out of {total_count}

### Key Risks and Considerations
[List any applicable risks and considerations]

---
*Report generated by Kanoo Ventures Investment Screening System*"""
    
    return await paradigm_client.chat_completion(report_prompt)