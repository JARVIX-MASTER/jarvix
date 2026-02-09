"""
JARVIX User Profile Module
Stores user personal data for auto-filling forms.
Data is saved locally in a JSON file.
"""

import os
import json
from pathlib import Path
from typing import Dict, Optional, Any


class UserProfile:
    """Manages user profile data for form auto-filling."""
    
    # Common form field mappings
    FIELD_MAPPINGS = {
        # Name variations
        'name': ['name', 'full_name', 'fullname', 'your_name', 'yourname', 'customer_name'],
        'first_name': ['first_name', 'firstname', 'fname', 'first'],
        'last_name': ['last_name', 'lastname', 'lname', 'last', 'surname'],
        
        # Contact
        'email': ['email', 'mail', 'email_address', 'emailaddress', 'e-mail', 'user_email'],
        'phone': ['phone', 'mobile', 'telephone', 'tel', 'phone_number', 'phonenumber', 'contact', 'cell'],
        
        # Address
        'address': ['address', 'street', 'street_address', 'address1', 'address_line_1'],
        'city': ['city', 'town', 'locality'],
        'state': ['state', 'province', 'region'],
        'pincode': ['pincode', 'zip', 'zipcode', 'zip_code', 'postal', 'postal_code', 'postcode'],
        'country': ['country', 'nation'],
        
        # Other
        'company': ['company', 'organization', 'org', 'company_name'],
        'username': ['username', 'user', 'login', 'user_name'],
    }
    
    def __init__(self):
        # Store in JARVIX data folder
        self.data_dir = Path(os.environ.get('APPDATA', '.')) / 'JARVIX'
        self.data_dir.mkdir(exist_ok=True)
        self.profile_path = self.data_dir / 'user_profile.json'
        self.profile = self._load_profile()
    
    def _load_profile(self) -> Dict[str, str]:
        """Load profile from disk."""
        if self.profile_path.exists():
            try:
                with open(self.profile_path, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_profile(self) -> bool:
        """Save profile to disk."""
        try:
            with open(self.profile_path, 'w') as f:
                json.dump(self.profile, f, indent=2)
            return True
        except Exception as e:
            print(f"❌ Failed to save profile: {e}")
            return False
    
    def set_field(self, field: str, value: str) -> bool:
        """Set a profile field."""
        field = field.lower().strip()
        self.profile[field] = value
        return self._save_profile()
    
    def get_field(self, field: str) -> Optional[str]:
        """Get a profile field."""
        return self.profile.get(field.lower().strip())
    
    def set_multiple(self, data: Dict[str, str]) -> bool:
        """Set multiple profile fields at once."""
        for field, value in data.items():
            self.profile[field.lower().strip()] = value
        return self._save_profile()
    
    def get_all(self) -> Dict[str, str]:
        """Get all profile fields."""
        return self.profile.copy()
    
    def clear(self) -> bool:
        """Clear all profile data."""
        self.profile = {}
        return self._save_profile()
    
    def get_form_data(self) -> Dict[str, str]:
        """
        Get form data with all possible field name variations.
        This creates a mapping that can match various form field names.
        """
        form_data = {}
        
        for standard_field, variations in self.FIELD_MAPPINGS.items():
            if standard_field in self.profile:
                value = self.profile[standard_field]
                # Add all variations
                for variation in variations:
                    form_data[variation] = value
        
        return form_data
    
    def get_display_profile(self) -> str:
        """Get a formatted string for display."""
        if not self.profile:
            return "No profile saved yet."
        
        lines = ["📋 Your Profile:\n"]
        for field, value in self.profile.items():
            # Mask sensitive data
            if 'password' in field.lower():
                display_value = "****"
            else:
                display_value = value
            lines.append(f"• {field.title()}: {display_value}")
        
        return "\n".join(lines)


# Singleton instance
user_profile = UserProfile()


# Simple wrapper functions
def save_profile_field(field: str, value: str) -> bool:
    """Save a single profile field."""
    return user_profile.set_field(field, value)


def save_profile(data: Dict[str, str]) -> bool:
    """Save multiple profile fields."""
    return user_profile.set_multiple(data)


def get_profile() -> Dict[str, str]:
    """Get all profile data."""
    return user_profile.get_all()


def get_form_data() -> Dict[str, str]:
    """Get form data with field variations."""
    return user_profile.get_form_data()


def get_profile_display() -> str:
    """Get formatted profile for display."""
    return user_profile.get_display_profile()


def clear_profile() -> bool:
    """Clear all profile data."""
    return user_profile.clear()
