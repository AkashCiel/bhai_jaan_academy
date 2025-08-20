from datetime import datetime
from typing import Dict, List

class MessageBuilder:
    @staticmethod
    def build_daily_report(users_processed: int, success_count: int, errors: List[str]) -> Dict:
        """Build daily scheduled run report message"""
        fields = [
            {'name': 'Users Processed', 'value': str(users_processed), 'inline': True},
            {'name': 'Success Rate', 'value': f'{success_count}/{users_processed}', 'inline': True}
        ]
        
        # Add errors field if there are any errors
        if errors:
            error_text = '\n'.join([f'• {error}' for error in errors])
            fields.append({'name': '❌ Errors', 'value': error_text, 'inline': False})
        
        return {
            'title': '📊 Daily Scheduled Run Report',
            'description': f'Processed {users_processed} users with {success_count} successful reports',
            'color': 0x00ff00 if not errors else 0xffaa00,  # Green if no errors, orange if errors
            'fields': fields
        }
    
    @staticmethod
    def build_error_alert(error_type: str, details: str) -> Dict:
        """Build error alert message"""
        return {
            'title': '🚨 CRITICAL SYSTEM ALERT',
            'description': f'{error_type}: {details}',
            'color': 0xff0000,  # Red
            'fields': [
                {'name': 'Timestamp', 'value': datetime.now().isoformat(), 'inline': False}
            ]
        }
