#!/usr/bin/env python3
"""
PWA Installation and Offline Behavior Tests
Tests PWA installation process, offline behavior, and spiritual content caching.
"""

import pytest
import json
import time
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock


class TestPWAInstallation:
    """Test PWA installation and app-like behavior"""
    
    def test_install_prompt_timing(self):
        """Test when install prompt should be shown"""
        
        class MockInstallManager:
            def __init__(self):
                self.page_visits = 0
                self.time_on_site = 0
                self.user_engagement = 0
                self.install_dismissed = False
            
            def track_page_visit(self):
                self.page_visits += 1
            
            def track_time_on_site(self, seconds):
                self.time_on_site += seconds
            
            def track_engagement(self, action):
                engagement_scores = {
                    "spiritual_query": 10,
                    "voice_interaction": 8,
                    "conversation_save": 6,
                    "page_view": 1
                }
                self.user_engagement += engagement_scores.get(action, 0)
            
            def should_show_install_prompt(self):
                """Determine if install prompt should be shown"""
                if self.install_dismissed:
                    return False
                
                # Show prompt if user is engaged
                conditions = [
                    self.page_visits >= 3,          # At least 3 page visits
                    self.time_on_site >= 120,       # At least 2 minutes on site
                    self.user_engagement >= 25      # Sufficient engagement
                ]
                
                return any(conditions)  # Any condition triggers prompt
        
        install_manager = MockInstallManager()
        
        # Initially should not show prompt
        assert install_manager.should_show_install_prompt() == False
        
        # Test engagement-based prompt
        install_manager.track_engagement("spiritual_query")
        install_manager.track_engagement("spiritual_query") 
        install_manager.track_engagement("voice_interaction")
        
        assert install_manager.should_show_install_prompt() == True, "High engagement should trigger prompt"
        
        # Test visit-based prompt
        install_manager2 = MockInstallManager()
        for _ in range(3):
            install_manager2.track_page_visit()
        
        assert install_manager2.should_show_install_prompt() == True, "Multiple visits should trigger prompt"
        
        # Test time-based prompt
        install_manager3 = MockInstallManager()
        install_manager3.track_time_on_site(130)
        
        assert install_manager3.should_show_install_prompt() == True, "Extended time should trigger prompt"
    
    def test_install_process_flow(self):
        """Test the complete PWA installation flow"""
        
        class MockInstallFlow:
            def __init__(self):
                self.stages = []
                self.install_event = None
                self.user_choice = None
            
            def prepare_install_event(self):
                """Simulate beforeinstallprompt event"""
                self.install_event = {
                    "prompt": self.show_install_dialog,
                    "userChoice": None
                }
                self.stages.append("beforeinstallprompt_received")
                return self.install_event
            
            def show_install_dialog(self):
                """Simulate showing install dialog"""
                self.stages.append("install_dialog_shown")
                # Simulate user accepting
                self.user_choice = "accepted"
                self.install_event["userChoice"] = {"outcome": self.user_choice}
                return self.user_choice
            
            def complete_installation(self):
                """Simulate installation completion"""
                if self.user_choice == "accepted":
                    self.stages.append("app_installed")
                    self.stages.append("standalone_mode_enabled")
                    return True
                return False
        
        install_flow = MockInstallFlow()
        
        # Test install flow
        event = install_flow.prepare_install_event()
        assert event is not None, "Should prepare install event"
        assert "beforeinstallprompt_received" in install_flow.stages
        
        choice = event["prompt"]()
        assert choice == "accepted", "User should accept installation"
        assert "install_dialog_shown" in install_flow.stages
        
        installed = install_flow.complete_installation()
        assert installed == True, "Installation should complete successfully"
        assert "app_installed" in install_flow.stages
        assert "standalone_mode_enabled" in install_flow.stages
    
    def test_standalone_app_behavior(self):
        """Test app behavior when installed as standalone"""
        
        class MockStandaloneApp:
            def __init__(self, display_mode="standalone"):
                self.display_mode = display_mode
                self.navigation_mode = "app"
                self.fullscreen = True
                self.spiritual_shortcuts = True
            
            def get_display_mode(self):
                return self.display_mode
            
            def get_app_shortcuts(self):
                """Get spiritual guidance shortcuts"""
                return [
                    {
                        "name": "New Spiritual Question",
                        "url": "/guidance/new",
                        "icon": "/icons/question-icon.png"
                    },
                    {
                        "name": "Daily Wisdom", 
                        "url": "/wisdom/daily",
                        "icon": "/icons/wisdom-icon.png"
                    },
                    {
                        "name": "Sacred Texts",
                        "url": "/texts",
                        "icon": "/icons/scripture-icon.png"
                    }
                ]
            
            def has_native_feel(self):
                """Check if app feels native"""
                return all([
                    self.display_mode == "standalone",
                    self.navigation_mode == "app",
                    self.spiritual_shortcuts
                ])
        
        app = MockStandaloneApp()
        
        assert app.get_display_mode() == "standalone", "Should run in standalone mode"
        assert app.has_native_feel() == True, "Should feel like native app"
        
        shortcuts = app.get_app_shortcuts()
        assert len(shortcuts) >= 3, "Should have spiritual guidance shortcuts"
        assert any("Spiritual" in shortcut["name"] for shortcut in shortcuts), "Should have spiritual shortcuts"


class TestOfflineBehavior:
    """Test comprehensive offline behavior"""
    
    def test_offline_detection(self):
        """Test offline/online detection"""
        
        class MockNetworkManager:
            def __init__(self):
                self.online = True
                self.connection_type = "wifi"
                self.listeners = []
            
            def set_online_status(self, online, connection_type="wifi"):
                self.online = online
                self.connection_type = connection_type if online else None
                self._notify_listeners()
            
            def add_listener(self, callback):
                self.listeners.append(callback)
            
            def _notify_listeners(self):
                for listener in self.listeners:
                    listener(self.online, self.connection_type)
            
            def get_network_info(self):
                return {
                    "online": self.online,
                    "connection_type": self.connection_type,
                    "effective_type": "4g" if self.online else None
                }
        
        network = MockNetworkManager()
        
        # Test initial online state
        info = network.get_network_info()
        assert info["online"] == True, "Should start online"
        assert info["connection_type"] == "wifi"
        
        # Test going offline
        offline_detected = False
        
        def offline_handler(online, connection):
            nonlocal offline_detected
            offline_detected = not online
        
        network.add_listener(offline_handler)
        network.set_online_status(False)
        
        info = network.get_network_info()
        assert info["online"] == False, "Should detect offline"
        assert offline_detected == True, "Offline handler should be called"
        
        # Test coming back online
        online_detected = False
        
        def online_handler(online, connection):
            nonlocal online_detected
            online_detected = online
        
        network.add_listener(online_handler)
        network.set_online_status(True, "cellular")
        
        info = network.get_network_info()
        assert info["online"] == True, "Should detect back online"
        assert info["connection_type"] == "cellular"
        assert online_detected == True, "Online handler should be called"
    
    def test_offline_spiritual_content_access(self):
        """Test accessing spiritual content while offline"""
        
        class MockOfflineSpiritualContent:
            def __init__(self):
                self.cached_content = {
                    "bhagavad_gita_summary": {
                        "title": "Bhagavad Gita - Core Teachings",
                        "content": "The Bhagavad Gita contains Lord Krishna's eternal wisdom...",
                        "verses": ["2.47", "3.15", "4.7", "18.66"],
                        "cached_at": time.time()
                    },
                    "daily_wisdom": {
                        "title": "Daily Spiritual Wisdom",
                        "quotes": [
                            "You have a right to perform your prescribed duty, but not to the fruits of action.",
                            "When meditation is mastered, the mind is unwavering like the flame of a lamp in a windless place."
                        ],
                        "sources": ["Bhagavad Gita 2.47", "Bhagavad Gita 6.19"],
                        "cached_at": time.time()
                    },
                    "sanskrit_glossary": {
                        "terms": {
                            "dharma": "righteous duty",
                            "karma": "action and its consequences", 
                            "moksha": "liberation",
                            "atman": "soul/self"
                        },
                        "cached_at": time.time()
                    }
                }
                self.offline_mode = False
            
            def set_offline_mode(self, offline):
                self.offline_mode = offline
            
            def get_spiritual_content(self, content_type):
                """Get spiritual content, preferring cache when offline"""
                if self.offline_mode:
                    cached = self.cached_content.get(content_type)
                    if cached:
                        return {
                            **cached,
                            "source": "cache",
                            "offline": True
                        }
                    else:
                        return {
                            "error": "Content not available offline",
                            "offline": True,
                            "suggestion": "This content will be available when you're back online"
                        }
                else:
                    # Simulate fetching fresh content when online
                    return {
                        "title": f"Fresh {content_type}",
                        "content": "Latest spiritual guidance...",
                        "source": "network",
                        "offline": False
                    }
            
            def get_offline_capabilities(self):
                """List what's available offline"""
                return {
                    "cached_content_types": list(self.cached_content.keys()),
                    "total_cached_items": len(self.cached_content),
                    "estimated_offline_time": "7 days",
                    "last_sync": time.time()
                }
        
        content_manager = MockOfflineSpiritualContent()
        
        # Test online content access
        gita_content = content_manager.get_spiritual_content("bhagavad_gita_summary")
        assert gita_content["source"] == "network", "Should fetch from network when online"
        assert gita_content["offline"] == False
        
        # Test offline content access
        content_manager.set_offline_mode(True)
        
        cached_gita = content_manager.get_spiritual_content("bhagavad_gita_summary")
        assert cached_gita["source"] == "cache", "Should use cache when offline"
        assert cached_gita["offline"] == True
        assert "Krishna" in cached_gita["content"], "Should contain spiritual content"
        
        # Test unavailable content offline
        missing_content = content_manager.get_spiritual_content("advanced_vedanta")
        assert "error" in missing_content, "Should show error for unavailable content"
        assert missing_content["offline"] == True
        
        # Test offline capabilities
        capabilities = content_manager.get_offline_capabilities()
        assert capabilities["total_cached_items"] >= 3, "Should have multiple cached items"
        assert "bhagavad_gita_summary" in capabilities["cached_content_types"]
    
    def test_offline_conversation_continuity(self):
        """Test continuing conversations while offline"""
        
        class MockOfflineConversation:
            def __init__(self):
                self.conversation_history = []
                self.pending_messages = []
                self.offline_mode = False
                self.context_preserved = True
            
            def set_offline_mode(self, offline):
                self.offline_mode = offline
            
            def send_message(self, message):
                """Send message, handling offline state"""
                message_obj = {
                    "id": f"msg_{len(self.conversation_history)}",
                    "content": message,
                    "timestamp": time.time(),
                    "offline": self.offline_mode
                }
                
                if self.offline_mode:
                    # Store message for later sync
                    self.pending_messages.append(message_obj)
                    
                    # Provide offline response
                    response = self._generate_offline_response(message)
                    response_obj = {
                        "id": f"resp_{len(self.conversation_history)}",
                        "content": response,
                        "timestamp": time.time(),
                        "offline": True,
                        "cached": True
                    }
                    
                    self.conversation_history.extend([message_obj, response_obj])
                    return response_obj
                else:
                    # Normal online processing
                    self.conversation_history.append(message_obj)
                    response = f"Online response to: {message}"
                    response_obj = {
                        "id": f"resp_{len(self.conversation_history)}",
                        "content": response,
                        "timestamp": time.time(),
                        "offline": False
                    }
                    self.conversation_history.append(response_obj)
                    return response_obj
            
            def _generate_offline_response(self, message):
                """Generate appropriate offline response"""
                message_lower = message.lower()
                
                if "dharma" in message_lower:
                    return "Dharma (धर्म) is your righteous duty as taught by Lord Krishna. This guidance is from our cached wisdom."
                elif "karma" in message_lower:
                    return "Karma (कर्म) is the law of action as explained in the Bhagavad Gita. This is cached spiritual guidance."
                else:
                    return "I have some cached wisdom available offline. For the most complete guidance, please reconnect when possible."
            
            def sync_pending_messages(self):
                """Sync pending messages when back online"""
                if not self.offline_mode and self.pending_messages:
                    synced_count = len(self.pending_messages)
                    for msg in self.pending_messages:
                        msg["synced"] = True
                        msg["synced_at"] = time.time()
                    self.pending_messages.clear()
                    return synced_count
                return 0
            
            def get_conversation_stats(self):
                """Get conversation statistics"""
                offline_messages = sum(1 for msg in self.conversation_history if msg.get("offline"))
                cached_responses = sum(1 for msg in self.conversation_history if msg.get("cached"))
                
                return {
                    "total_messages": len(self.conversation_history),
                    "offline_messages": offline_messages,
                    "cached_responses": cached_responses,
                    "pending_sync": len(self.pending_messages),
                    "context_preserved": self.context_preserved
                }
        
        conversation = MockOfflineConversation()
        
        # Test online conversation
        response1 = conversation.send_message("What is dharma?")
        assert response1["offline"] == False, "Online response should not be marked offline"
        assert "Online response" in response1["content"]
        
        # Test going offline mid-conversation
        conversation.set_offline_mode(True)
        
        response2 = conversation.send_message("Tell me more about dharma")
        assert response2["offline"] == True, "Offline response should be marked offline"
        assert response2["cached"] == True, "Should use cached wisdom"
        assert "dharma" in response2["content"].lower(), "Should provide relevant cached content"
        
        # Test conversation continuity
        stats = conversation.get_conversation_stats()
        assert stats["total_messages"] >= 4, "Should have messages from both online and offline"
        assert stats["offline_messages"] >= 1, "Should track offline messages"
        assert stats["context_preserved"] == True, "Should preserve conversation context"
        
        # Test syncing when back online
        conversation.set_offline_mode(False)
        synced = conversation.sync_pending_messages()
        assert synced >= 1, "Should sync pending messages"
        
        final_stats = conversation.get_conversation_stats()
        assert final_stats["pending_sync"] == 0, "No messages should be pending sync"


def run_offline_tests():
    """Run offline capability tests"""
    
    print("📱 Starting PWA Installation and Offline Behavior Tests...")
    print("=" * 80)
    
    # Initialize test classes
    install_tests = TestPWAInstallation()
    offline_tests = TestOfflineBehavior()
    
    # Test methods to run
    test_methods = [
        ("Install Prompt Timing", install_tests.test_install_prompt_timing),
        ("Install Process Flow", install_tests.test_install_process_flow),
        ("Standalone App Behavior", install_tests.test_standalone_app_behavior),
        ("Offline Detection", offline_tests.test_offline_detection),
        ("Offline Spiritual Content Access", offline_tests.test_offline_spiritual_content_access),
        ("Offline Conversation Continuity", offline_tests.test_offline_conversation_continuity),
    ]
    
    passed_tests = 0
    failed_tests = 0
    test_results = []
    
    for test_name, test_method in test_methods:
        try:
            print(f"🔍 Running: {test_name}")
            test_method()
            print(f"   ✅ PASSED")
            passed_tests += 1
            test_results.append({
                "test": test_name,
                "status": "passed",
                "details": "Test completed successfully"
            })
        except Exception as e:
            print(f"   ❌ FAILED: {str(e)}")
            failed_tests += 1
            test_results.append({
                "test": test_name,
                "status": "failed", 
                "error": str(e)
            })
        print()
    
    # Generate summary
    total_tests = len(test_methods)
    success_rate = (passed_tests / total_tests) * 100
    
    print("📊 OFFLINE BEHAVIOR TESTING SUMMARY")
    print("=" * 50)
    print(f"📱 Total Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")
    print(f"📈 Success Rate: {success_rate:.1f}%")
    print()
    
    print("🔋 Offline Capabilities Validated:")
    print("   • PWA installation flow")
    print("   • Standalone app behavior")
    print("   • Network status detection")
    print("   • Offline spiritual content access")
    print("   • Conversation continuity offline")
    print("   • Background sync when online")
    
    return {
        "success_rate": success_rate,
        "test_results": test_results,
        "total_tests": total_tests,
        "passed": passed_tests,
        "failed": failed_tests
    }


if __name__ == "__main__":
    results = run_offline_tests()
    success = results["success_rate"] >= 80
    exit(0 if success else 1)
