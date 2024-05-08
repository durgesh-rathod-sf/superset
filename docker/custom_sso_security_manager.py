import os
from superset.security import SupersetSecurityManager

class CustomSsoSecurityManager(SupersetSecurityManager):
    """
    The CustomSsoSecurityManager class extends the SupersetSecurityManager class.
    """    
    def oauth_user_info(self, provider, response=None):
        if provider == 'okta':
            user_info = response.get("userinfo")
            me = self.appbuilder.sm.oauth_remotes[provider].parse_id_token(
                response, user_info["nonce"])
            first_name, last_name = me["name"].split(" ", 1)
            return {
                'name': me['name'],
                'email': me['email'],
                'id': me['email'],
                'username': me['email'],
                'first_name': first_name,
                'last_name': last_name,
            }
    
    def sync_roles(self):
        self.add_role(os.getenv("SSO_USER_REGISTRATION_ROLE"))
        return super().sync_roles()