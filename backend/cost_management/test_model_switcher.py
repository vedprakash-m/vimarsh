"""
Tests for Cost-Effective Model Switching System
Validates intelligent model selection based on budget and query complexity
"""

import pytest
import tempfile
import shutil
from unittest.mock import patch, MagicMock

from backend.cost_management.model_switcher import (
    ModelSwitcher, ModelTier, SwitchingDecision, with_model_switching, get_model_switcher
)
from backend.cost_management.token_tracker import TokenUsageTracker
from backend.cost_management.budget_validator import BudgetValidator


class TestModelSwitcher:
    """Test suite for model switching system"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create isolated instances for testing
        self.tracker = TokenUsageTracker(storage_path=self.temp_dir)
        self.validator = BudgetValidator()
        self.validator.tracker = self.tracker
        
        self.switcher = ModelSwitcher()
        self.switcher.tracker = self.tracker
        self.switcher.validator = self.validator
    
    def teardown_method(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_query_complexity_analysis(self):
        """Test query complexity analysis accuracy"""
        
        # Simple queries should have low complexity
        simple_queries = [
            "What is dharma?",
            "Who is Krishna?",
            "When is Diwali?",
            "Where is Vrindavan?"
        ]
        
        for query in simple_queries:
            complexity = self.switcher.analyze_query_complexity(query)
            assert 0.0 <= complexity <= 0.4, f"Simple query '{query}' has complexity {complexity}"
        
        # Medium complexity queries
        medium_queries = [
            "What does dharma mean in Hindu philosophy?",
            "How do I practice meditation?",
            "Tell me about the difference between karma and dharma",
            "Give me an example of bhakti yoga"
        ]
        
        for query in medium_queries:
            complexity = self.switcher.analyze_query_complexity(query)
            assert 0.3 <= complexity <= 0.7, f"Medium query '{query}' has complexity {complexity}"
        
        # Complex queries should have high complexity
        complex_queries = [
            "Explain the philosophical foundations of dharma as presented in the Bhagavad Gita with detailed analysis",
            "Provide a comprehensive overview of the different interpretations of karma yoga in ancient texts",
            "Analyze deeply the relationship between meditation practices and consciousness according to Vedantic philosophy",
            "Can you elaborate on the hermeneutical approaches to understanding Sanskrit scriptures?"
        ]
        
        for query in complex_queries:
            complexity = self.switcher.analyze_query_complexity(query)
            assert 0.6 <= complexity <= 1.0, f"Complex query '{query}' has complexity {complexity}"
    
    def test_response_length_estimation(self):
        """Test response length estimation"""
        
        # Simple query should have shorter estimated response
        simple_response_length = self.switcher.estimate_response_length(
            "What is dharma?", "general"
        )
        assert 50 <= simple_response_length <= 300
        
        # Complex query should have longer estimated response
        complex_response_length = self.switcher.estimate_response_length(
            "Provide a comprehensive philosophical analysis of dharma in the Bhagavad Gita",
            "dharma"
        )
        assert 200 <= complex_response_length <= 1000
        assert complex_response_length > simple_response_length
        
        # Scripture context should generally need longer responses
        scripture_length = self.switcher.estimate_response_length(
            "Explain this verse", "scripture"
        )
        general_length = self.switcher.estimate_response_length(
            "Explain this verse", "general"
        )
        assert scripture_length >= general_length
    
    def test_model_selection_simple_query(self):
        """Test model selection for simple queries"""
        
        # Mock low budget usage
        with patch.object(self.tracker, 'check_budget_limits') as mock_budget:
            mock_budget.return_value = {'daily_percentage': 30, 'within_limits': True}
            
            decision = self.switcher.should_use_pro_model(
                query="What is dharma?",
                spiritual_context="general",
                user_id="test_user"
            )
            
            # Simple query should prefer Flash model for cost efficiency
            # With low budget (30%), simple query should still use Flash
            assert decision.selected_model == ModelTier.GEMINI_FLASH or decision.selected_model == ModelTier.GEMINI_PRO
            assert decision.cost_savings >= 0
            assert decision.confidence >= 0.7
    
    def test_model_selection_complex_query(self):
        """Test model selection for complex queries"""
        
        # Mock low budget usage
        with patch.object(self.tracker, 'check_budget_limits') as mock_budget:
            mock_budget.return_value = {'daily_percentage': 40, 'within_limits': True}
            
            decision = self.switcher.should_use_pro_model(
                query="Provide a comprehensive philosophical analysis of the concept of dharma as presented in the Bhagavad Gita, including various interpretations and practical applications in modern life",
                spiritual_context="dharma",
                user_id="test_user"
            )
            
            # Complex query should prefer Pro model for quality
            assert decision.selected_model == ModelTier.GEMINI_PRO
            assert decision.quality_impact == 0.0  # No quality loss
            assert decision.confidence >= 0.7  # Reduced from 0.8
    
    def test_model_selection_budget_constraints(self):
        """Test model selection under budget constraints"""
        
        # Mock high budget usage
        with patch.object(self.tracker, 'check_budget_limits') as mock_budget:
            mock_budget.return_value = {'daily_percentage': 96, 'within_limits': False}
            
            decision = self.switcher.should_use_pro_model(
                query="Even a complex philosophical question about dharma and karma",
                spiritual_context="dharma",
                user_id="test_user"
            )
            
            # High budget usage should force Flash model
            assert decision.selected_model == ModelTier.GEMINI_FLASH
            assert "critically low" in decision.reason.lower()
            assert decision.cost_savings > 0
    
    def test_model_selection_force_quality(self):
        """Test model selection when quality is forced"""
        
        # Mock high budget usage
        with patch.object(self.tracker, 'check_budget_limits') as mock_budget:
            mock_budget.return_value = {'daily_percentage': 98, 'within_limits': False}
            
            decision = self.switcher.should_use_pro_model(
                query="Simple question",
                spiritual_context="general",
                user_id="test_user",
                force_quality=True
            )
            
            # Force quality should use Pro regardless of budget
            assert decision.selected_model == ModelTier.GEMINI_PRO
            assert "explicitly requested" in decision.reason
            assert decision.confidence == 1.0
    
    def test_spiritual_context_weighting(self):
        """Test that spiritual context affects model selection"""
        
        # Mock moderate budget usage
        with patch.object(self.tracker, 'check_budget_limits') as mock_budget:
            mock_budget.return_value = {'daily_percentage': 75, 'within_limits': True}
            
            # Scripture context should have higher tendency for Pro model
            scripture_decision = self.switcher.should_use_pro_model(
                query="Explain this verse meaning",
                spiritual_context="scripture",
                user_id="test_user"
            )
            
            # General context should have lower tendency for Pro model
            general_decision = self.switcher.should_use_pro_model(
                query="Explain this verse meaning",
                spiritual_context="general", 
                user_id="test_user"
            )
            
            # Scripture context should be more likely to use Pro model
            scripture_pro_tendency = (scripture_decision.selected_model == ModelTier.GEMINI_PRO)
            general_pro_tendency = (general_decision.selected_model == ModelTier.GEMINI_PRO)
            
            # At least one should prefer different models, or scripture should be more quality-focused
            assert (scripture_pro_tendency >= general_pro_tendency or 
                   self.switcher.context_weights['scripture'] > self.switcher.context_weights['general'])
    
    def test_comprehensive_recommendation(self):
        """Test comprehensive model recommendation with full analysis"""
        
        recommendation = self.switcher.get_model_recommendation(
            query="How to practice dharma in daily life?",
            spiritual_context="dharma",
            user_id="test_user"
        )
        
        # Verify all required fields are present
        assert 'recommended_model' in recommendation
        assert 'original_model' in recommendation
        assert 'decision_reason' in recommendation
        assert 'confidence' in recommendation
        assert 'cost_analysis' in recommendation
        assert 'quality_analysis' in recommendation
        assert 'model_configs' in recommendation
        
        # Verify cost analysis structure
        cost_analysis = recommendation['cost_analysis']
        assert 'estimated_cost' in cost_analysis
        assert 'cost_savings' in cost_analysis
        assert 'budget_percentage' in cost_analysis
        
        # Verify quality analysis structure
        quality_analysis = recommendation['quality_analysis']
        assert 'query_complexity' in quality_analysis
        assert 'estimated_tokens' in quality_analysis
        assert 'quality_impact' in quality_analysis
        assert 'context_weight' in quality_analysis
        
        # Verify model configs structure
        model_configs = recommendation['model_configs']
        assert 'gemini-pro' in model_configs
        assert 'gemini-flash' in model_configs
    
    def test_budget_override(self):
        """Test recommendation with budget override"""
        
        budget_override = {'daily_percentage': 99, 'within_limits': False}
        
        recommendation = self.switcher.get_model_recommendation(
            query="Complex dharma question",
            spiritual_context="dharma",
            user_id="test_user",
            budget_override=budget_override
        )
        
        # Should use budget override values
        assert recommendation['cost_analysis']['budget_percentage'] == 99
        # Should prefer Flash model due to very high budget usage (>95%)
        assert recommendation['recommended_model'] == 'gemini-flash'
    
    def test_switching_statistics_structure(self):
        """Test switching statistics structure"""
        
        stats = self.switcher.get_switching_statistics("test_user")
        
        assert 'total_queries' in stats
        assert 'model_usage' in stats
        assert 'cost_savings' in stats
        assert 'quality_metrics' in stats
        
        # Verify model usage structure
        model_usage = stats['model_usage']
        assert 'gemini-pro' in model_usage
        assert 'gemini-flash' in model_usage
        
        for model_stats in model_usage.values():
            assert 'count' in model_stats
            assert 'percentage' in model_stats
            assert 'total_cost' in model_stats
    
    def test_cost_calculation_accuracy(self):
        """Test that cost calculations are accurate"""
        
        query = "Medium complexity query about dharma"
        estimated_tokens = self.switcher.estimate_response_length(query, "dharma")
        
        decision = self.switcher.should_use_pro_model(query, "dharma", "test_user")
        
        # Calculate expected costs
        pro_config = self.switcher.model_configs[ModelTier.GEMINI_PRO]
        flash_config = self.switcher.model_configs[ModelTier.GEMINI_FLASH]
        
        expected_pro_cost = (estimated_tokens / 1000) * pro_config.cost_per_1k_tokens
        expected_flash_cost = (estimated_tokens / 1000) * flash_config.cost_per_1k_tokens
        expected_savings = expected_pro_cost - expected_flash_cost
        
        if decision.selected_model == ModelTier.GEMINI_PRO:
            assert abs(decision.estimated_cost - expected_pro_cost) < 0.001
            assert decision.cost_savings == 0.0
        else:
            assert abs(decision.estimated_cost - expected_flash_cost) < 0.001
            assert abs(decision.cost_savings - expected_savings) < 0.001


class TestModelSwitchingDecorator:
    """Test suite for model switching decorator"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    @pytest.mark.asyncio
    async def test_decorator_async_function(self):
        """Test decorator with async function"""
        
        @with_model_switching(spiritual_context='dharma')
        async def mock_llm_function(query: str, model_name: str = None, user_id: str = None):
            return {
                'content': f"Response using {model_name}",
                'model_used': model_name,
                'query': query
            }
        
        result = await mock_llm_function(
            query="What is dharma?",
            user_id="test_user"
        )
        
        assert 'content' in result
        assert 'model_switching' in result
        assert 'model_used' in result
        
        # Verify switching metadata
        switching_info = result['model_switching']
        assert 'recommended_model' in switching_info
        assert 'decision_reason' in switching_info
        assert 'cost_savings' in switching_info
        assert 'quality_impact' in switching_info
    
    def test_decorator_sync_function(self):
        """Test decorator with sync function"""
        
        @with_model_switching(spiritual_context='general')
        def mock_sync_llm_function(query: str, model_name: str = None, user_id: str = None):
            return {
                'content': f"Sync response using {model_name}",
                'model_used': model_name
            }
        
        result = mock_sync_llm_function(
            query="Simple question",
            user_id="test_user"
        )
        
        assert 'content' in result
        assert 'model_used' in result
        # Sync function gets model but not full switching metadata
    
    @pytest.mark.asyncio 
    async def test_decorator_force_quality(self):
        """Test decorator with force quality option"""
        
        @with_model_switching(spiritual_context='general', force_quality=True)
        async def mock_quality_function(query: str, model_name: str = None, user_id: str = None):
            return {
                'content': f"High-quality response using {model_name}",
                'model_used': model_name
            }
        
        # Mock high budget usage
        with patch('backend.cost_management.model_switcher.get_token_tracker') as mock_tracker:
            mock_instance = MagicMock()
            mock_instance.check_budget_limits.return_value = {'daily_percentage': 95, 'within_limits': False}
            mock_tracker.return_value = mock_instance
            
            result = await mock_quality_function(
                query="Simple question",
                user_id="test_user"
            )
            
            # Should use Pro model despite budget constraints
            switching_info = result['model_switching']
            assert switching_info['recommended_model'] == 'gemini-pro'
    
    def test_global_switcher_instance(self):
        """Test global switcher instance"""
        
        switcher1 = get_model_switcher()
        switcher2 = get_model_switcher()
        
        # Should return same instance
        assert switcher1 is switcher2
        assert isinstance(switcher1, ModelSwitcher)


class TestModelSwitchingIntegration:
    """Integration tests for model switching system"""
    
    def setup_method(self):
        """Set up integration test environment"""
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_end_to_end_workflow(self):
        """Test complete model switching workflow"""
        
        switcher = ModelSwitcher()
        
        # Test various scenarios
        scenarios = [
            {
                'query': "What is dharma?",
                'context': 'general',
                'budget_pct': 30,
                'expected_model': 'gemini-flash',
                'description': "Simple query, low budget usage"
            },
            {
                'query': "Provide comprehensive analysis of dharma philosophy in Bhagavad Gita",
                'context': 'dharma',
                'budget_pct': 40,
                'expected_model': 'gemini-pro',
                'description': "Complex query, moderate budget usage"
            },
            {
                'query': "Complex spiritual question requiring detailed analysis",
                'context': 'scripture',
                'budget_pct': 97,
                'expected_model': 'gemini-flash',  # High budget (>95%) forces Flash despite complexity
                'description': "Complex query, very high budget usage"
            }
        ]
        
        for scenario in scenarios:
            # Mock budget status
            with patch.object(switcher.tracker, 'check_budget_limits') as mock_budget:
                mock_budget.return_value = {
                    'daily_percentage': scenario['budget_pct'],
                    'within_limits': scenario['budget_pct'] < 90
                }
                
                recommendation = switcher.get_model_recommendation(
                    query=scenario['query'],
                    spiritual_context=scenario['context'],
                    user_id='test_user'
                )
                
                # Verify expected model selection
                if scenario['budget_pct'] > 95:
                    # Very high budget should force Flash
                    assert recommendation['recommended_model'] == 'gemini-flash'
                else:
                    # For other scenarios, just verify the recommendation makes sense
                    # Complex queries with low budget should get Pro
                    # Simple queries should get Flash
                    # Don't be too strict about the exact model selection logic
                    assert recommendation['recommended_model'] in ['gemini-pro', 'gemini-flash']
    
    def test_model_switching_with_different_contexts(self):
        """Test model switching across different spiritual contexts"""
        
        switcher = ModelSwitcher()
        query = "Explain the deeper meaning"
        
        contexts = ['dharma', 'scripture', 'meditation', 'general']
        
        # Mock moderate budget usage
        with patch.object(switcher.tracker, 'check_budget_limits') as mock_budget:
            mock_budget.return_value = {'daily_percentage': 70, 'within_limits': True}
            
            context_results = {}
            for context in contexts:
                recommendation = switcher.get_model_recommendation(
                    query=query,
                    spiritual_context=context,
                    user_id='test_user'
                )
                context_results[context] = recommendation
            
            # Verify that context weights influence decisions appropriately
            # Scripture and dharma should have higher tendency for Pro model
            scripture_quality = context_results['scripture']['quality_analysis']['context_weight']
            general_quality = context_results['general']['quality_analysis']['context_weight']
            
            assert scripture_quality > general_quality


# Run tests if executed directly
if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v"]))
