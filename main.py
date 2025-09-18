#!/usr/bin/env python3
"""
Investment Opportunity Screening System
Main entry point for the application
"""

import asyncio
import sys
import logging
from workflows.investment_screening import execute_workflow

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def main():
    """Main function to run the investment screening workflow"""
    try:
        # You can modify this to accept command line arguments or user input
        user_input = "Analyze the attached investment opportunity document"
        
        logger.info("Starting investment opportunity screening...")
        result = await execute_workflow(user_input)
        
        print("\n" + "="*80)
        print("INVESTMENT SCREENING REPORT")
        print("="*80)
        print(result)
        print("="*80)
        
    except Exception as e:
        logger.error(f"Error in main workflow: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())