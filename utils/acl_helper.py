"""
Phase 3: ACL Helper Utilities

Application-level permission checking (defense in depth).
Complements PostgreSQL RLS (ADR-012).
"""

from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class ACLHelper:
    """Helper functions for ACL validation and permission checks."""
    
    def __init__(self, supabase_client):
        """
        Initialize ACL helper.
        
        Args:
            supabase_client: Supabase client (with user JWT)
        """
        self.supabase = supabase_client
    
    async def user_can_access_document(
        self,
        user_id: str,
        document_id: str
    ) -> bool:
        """
        Check if user can access document.
        
        Application-level check (in addition to RLS).
        Used for explicit validation before expensive operations.
        
        Args:
            user_id: User UUID
            document_id: Document UUID
            
        Returns:
            True if user can access, False otherwise
        """
        try:
            # Query with user's JWT (RLS enforced)
            result = self.supabase.table('documents')\
                .select('id')\
                .eq('id', document_id)\
                .execute()
            
            # If RLS allows, result will contain the document
            return len(result.data) > 0
            
        except Exception as e:
            logger.error(f"Access check failed: {e}")
            return False
    
    async def get_user_teams(self, user_id: str) -> List[str]:
        """
        Get all team IDs user belongs to.
        
        Useful for caching and permission checks.
        
        Args:
            user_id: User UUID
            
        Returns:
            List of team UUIDs
        """
        try:
            result = self.supabase.table('team_members')\
                .select('team_id')\
                .eq('user_id', user_id)\
                .execute()
            
            return [row['team_id'] for row in result.data]
            
        except Exception as e:
            logger.error(f"Failed to get user teams: {e}")
            return []
    
    async def filter_documents_by_permission(
        self,
        user_id: str,
        document_ids: List[str]
    ) -> List[str]:
        """
        Filter document list to only authorized documents.
        
        Args:
            user_id: User UUID
            document_ids: List of document UUIDs
            
        Returns:
            Filtered list of document UUIDs user can access
        """
        if not document_ids:
            return []
        
        try:
            # Query with user's JWT (RLS filters)
            result = self.supabase.table('documents')\
                .select('id')\
                .in_('id', document_ids)\
                .execute()
            
            return [row['id'] for row in result.data]
            
        except Exception as e:
            logger.error(f"Permission filtering failed: {e}")
            return []
    
    async def grant_permission(
        self,
        document_id: str,
        user_id: str,
        granted_by: str,
        permission: str = 'read'
    ) -> bool:
        """
        Grant explicit permission to user.
        
        Args:
            document_id: Document UUID
            user_id: User to grant permission to
            granted_by: User granting the permission (must be owner)
            permission: Permission level (read, write, admin)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.supabase.table('document_permissions').insert({
                'document_id': document_id,
                'user_id': user_id,
                'permission': permission,
                'granted_by': granted_by
            }).execute()
            
            logger.info(
                f"Granted {permission} on {document_id} to user {user_id}"
            )
            return True
            
        except Exception as e:
            logger.error(f"Failed to grant permission: {e}")
            return False
    
    async def revoke_permission(
        self,
        document_id: str,
        user_id: str
    ) -> bool:
        """
        Revoke user's explicit permission.
        
        Args:
            document_id: Document UUID
            user_id: User to revoke permission from
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.supabase.table('document_permissions')\
                .delete()\
                .eq('document_id', document_id)\
                .eq('user_id', user_id)\
                .execute()
            
            logger.info(f"Revoked permission on {document_id} from user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to revoke permission: {e}")
            return False
