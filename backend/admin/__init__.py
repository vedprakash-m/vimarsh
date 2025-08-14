"""
Admin module for Vimarsh
Provides administrative capabilities for cost management and user administration
"""

from .admin_endpoints import (
    admin_cost_dashboard,
    admin_user_management,
    admin_budget_management,
    super_admin_role_management,
    admin_system_health,
    admin_get_user_role,
    admin_metrics_dashboard,
    admin_performance_report,
    admin_real_time_metrics,
    admin_alerts_dashboard,
    # Consolidated functions from refactoring
    admin_personalities_management,
    admin_content_sources,
    admin_content_management,
    get_content_status,
    acquire_personality_content,
    process_personality_content,
    validate_content_quality,
    create_personality_content_associations
)

__all__ = [
    'admin_cost_dashboard',
    'admin_user_management', 
    'admin_budget_management',
    'super_admin_role_management',
    'admin_system_health',
    'admin_get_user_role',
    'admin_metrics_dashboard',
    'admin_performance_report',
    'admin_real_time_metrics',
    'admin_alerts_dashboard',
    # Consolidated functions
    'admin_personalities_management',
    'admin_content_sources', 
    'admin_content_management',
    'get_content_status',
    'acquire_personality_content',
    'process_personality_content',
    'validate_content_quality',
    'create_personality_content_associations'
]
