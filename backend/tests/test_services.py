import pytest
import pandas as pd
from backend.services.activity_service import plan_outdoor_activity
from backend.services.exposure_service import calculate_exposure_score, compute_exposure_scores
from backend.services.summary_service import generate_daily_summary

def test_activity_advisor_avoids_spikes():
    # Simulate a spike in the middle of the day
    forecasts = [
        {'hour_offset': 1, 'category': 'Good', 'time': '8 AM'},
        {'hour_offset': 2, 'category': 'Moderate', 'time': '9 AM'},
        {'hour_offset': 3, 'category': 'Hazardous', 'time': '10 AM'},
        {'hour_offset': 4, 'category': 'Hazardous', 'time': '11 AM'},
        {'hour_offset': 5, 'category': 'Good', 'time': '12 PM'}
    ]
    
    # User wants to go out for 60 mins (1 hour window)
    result = plan_outdoor_activity(forecasts, 60)
    
    # Best window should avoid the 10 AM / 11 AM spike completely.
    # The best 1hr block is the 8 AM (Good) or 12 PM (Good).
    # Since it iterates, it might pick 8 AM or 12 PM. Either way, it must NOT pick 10 AM or 11 AM.
    assert result['best_time'] in ['8 AM to 9 AM', '12 PM to Late']
    assert '10 AM' in result['avoid_time'] or '11 AM' in result['avoid_time']

def test_exposure_score_severity():
    good_day = [
        {'horizon': 1, 'category': 'Good'},
        {'horizon': 4, 'category': 'Good'},
        {'horizon': 6, 'category': 'Good'},
        {'horizon': 12, 'category': 'Good'},
        {'horizon': 24, 'category': 'Good'}
    ]
    
    hazardous_day = [
        {'horizon': 1, 'category': 'Hazardous'},
        {'horizon': 4, 'category': 'Hazardous'},
        {'horizon': 6, 'category': 'Hazardous'},
        {'horizon': 12, 'category': 'Hazardous'},
        {'horizon': 24, 'category': 'Hazardous'}
    ]
    
    good_score = calculate_exposure_score(good_day)
    hazardous_score = calculate_exposure_score(hazardous_day)
    
    assert good_score == 0
    assert hazardous_score == 100
    
def test_daily_summary_changes_by_profile():
    forecast = [
        {'horizon': 1, 'category': 'Unhealthy', 'time': '9 AM'},
        {'horizon': 4, 'category': 'Moderate', 'time': '12 PM'}
    ]
    
    general_summary = generate_daily_summary(forecast, 'General')
    asthma_summary = generate_daily_summary(forecast, 'Asthma')
    
    # Asthma summary should include sensitive groups warning
    assert "Sensitive groups" not in general_summary
    assert "Sensitive groups" in asthma_summary
