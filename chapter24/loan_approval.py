"""
DISCLAIMER: This code is provided as part of a book as a coding exercise 
and does not reflect a real loan approval process. Do not use this for 
actual financial decisions.
"""

def loan_approval(debt_to_income_ratio, credit_score):
    """
    Determines loan approval status based on debt-to-income ratio and credit score.
    
    Args:
        debt_to_income_ratio (float): Debt to income ratio (0.0 to 1.0+)
        credit_score (int): Credit score (300-850)
    
    Returns:
        str: "Approved", "Denied", or "AdditionalReview"
    """
    if not isinstance(credit_score, int) or not (300 <= credit_score <= 850):
        raise ValueError("Credit score must be an integer between 300 and 850")
    
    if credit_score < 600 and debt_to_income_ratio > 0.5:
        return "Denied"
    elif credit_score >= 600 and debt_to_income_ratio < 0.5:
        return "Approved"
    else:
        return "AdditionalReview"
