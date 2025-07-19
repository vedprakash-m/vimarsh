"""
Local Test Server for Admin Features
Simple HTTP server to test admin endpoints locally
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
import logging
from datetime import datetime

# Import our admin modules
from core.user_roles import admin_role_manager, UserRole
from core.token_tracker import token_tracker
from core.budget_validator import budget_validator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdminTestHandler(BaseHTTPRequestHandler):
    """HTTP handler for testing admin features"""
    
    def do_GET(self):
        """Handle GET requests"""
        try:
            parsed_path = urllib.parse.urlparse(self.path)
            path = parsed_path.path
            
            if path == '/':
                self.send_html_dashboard()
            elif path == '/api/admin/cost-dashboard':
                self.send_cost_dashboard()
            elif path == '/api/admin/users':
                self.send_user_list()
            elif path == '/api/admin/health':
                self.send_health_status()
            elif path.startswith('/api/user/budget'):
                self.send_user_budget()
            else:
                self.send_404()
                
        except Exception as e:
            logger.error(f"Error handling GET request: {e}")
            self.send_error_response(str(e))
    
    def do_POST(self):
        """Handle POST requests"""
        try:
            parsed_path = urllib.parse.urlparse(self.path)
            path = parsed_path.path
            
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            if path == '/api/spiritual_guidance':
                self.handle_spiritual_guidance(post_data)
            elif path.startswith('/api/admin/users/') and path.endswith('/block'):
                self.handle_user_block(path)
            elif path.startswith('/api/admin/users/') and path.endswith('/unblock'):
                self.handle_user_unblock(path)
            elif path == '/api/admin/budgets':
                self.handle_budget_create(post_data)
            else:
                self.send_404()
                
        except Exception as e:
            logger.error(f"Error handling POST request: {e}")
            self.send_error_response(str(e))
    
    def send_html_dashboard(self):
        """Send HTML dashboard for testing"""
        html = """
<!DOCTYPE html>
<html>
<head>
    <title>Vimarsh Admin Features Test</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .section { border: 1px solid #ddd; margin: 10px 0; padding: 15px; }
        .admin { background: #f0f8ff; }
        .user { background: #f8fff0; }
        button { padding: 8px 15px; margin: 5px; cursor: pointer; }
        .admin-btn { background: #4CAF50; color: white; border: none; }
        .user-btn { background: #2196F3; color: white; border: none; }
        pre { background: #f5f5f5; padding: 10px; overflow-x: auto; }
        #response { border: 1px solid #ccc; padding: 10px; margin-top: 10px; }
    </style>
</head>
<body>
    <h1>🔐 Vimarsh Admin Features Test Dashboard</h1>
    
    <div class="section admin">
        <h2>👑 Admin Features (vedprakash.m@outlook.com)</h2>
        <button class="admin-btn" onclick="testAdminDashboard()">Cost Dashboard</button>
        <button class="admin-btn" onclick="testUserList()">List Users</button>
        <button class="admin-btn" onclick="testSystemHealth()">System Health</button>
        <button class="admin-btn" onclick="testBlockUser()">Block Test User</button>
        <button class="admin-btn" onclick="testUnblockUser()">Unblock Test User</button>
    </div>
    
    <div class="section user">
        <h2>👤 User Features (test@example.com)</h2>
        <button class="user-btn" onclick="testUserBudget()">My Budget Status</button>
        <button class="user-btn" onclick="testSpiritualGuidance()">Spiritual Guidance</button>
        <button class="user-btn" onclick="testTokenUsage()">Simulate Token Usage</button>
    </div>
    
    <div class="section">
        <h2>📊 Live Admin Data</h2>
        <button onclick="refreshData()">Refresh Data</button>
        <div id="liveData"></div>
    </div>
    
    <div id="response">
        <h3>Response:</h3>
        <pre id="responseContent">Click any button to see results...</pre>
    </div>

    <script>
        async function makeRequest(url, method = 'GET', body = null, headers = {}) {
            try {
                const options = { method, headers };
                if (body) {
                    options.body = JSON.stringify(body);
                    options.headers['Content-Type'] = 'application/json';
                }
                
                const response = await fetch(url, options);
                const data = await response.json();
                
                document.getElementById('responseContent').textContent = 
                    JSON.stringify(data, null, 2);
                    
                return data;
            } catch (error) {
                document.getElementById('responseContent').textContent = 
                    'Error: ' + error.message;
            }
        }
        
        // Admin functions
        async function testAdminDashboard() {
            await makeRequest('/api/admin/cost-dashboard', 'GET', null, {
                'x-user-email': 'vedprakash.m@outlook.com'
            });
        }
        
        async function testUserList() {
            await makeRequest('/api/admin/users', 'GET', null, {
                'x-user-email': 'vedprakash.m@outlook.com'
            });
        }
        
        async function testSystemHealth() {
            await makeRequest('/api/admin/health', 'GET', null, {
                'x-user-email': 'vedprakash.m@outlook.com'
            });
        }
        
        async function testBlockUser() {
            await makeRequest('/api/admin/users/test_user/block', 'POST', {}, {
                'x-user-email': 'vedprakash.m@outlook.com'
            });
        }
        
        async function testUnblockUser() {
            await makeRequest('/api/admin/users/test_user/unblock', 'POST', {}, {
                'x-user-email': 'vedprakash.m@outlook.com'
            });
        }
        
        // User functions
        async function testUserBudget() {
            await makeRequest('/api/user/budget', 'GET', null, {
                'x-user-email': 'test@example.com',
                'x-user-id': 'test_user'
            });
        }
        
        async function testSpiritualGuidance() {
            await makeRequest('/api/spiritual_guidance', 'POST', {
                query: "What is the meaning of dharma?",
                language: "English"
            }, {
                'x-user-email': 'test@example.com',
                'x-user-id': 'test_user',
                'x-session-id': 'session_123'
            });
        }
        
        async function testTokenUsage() {
            // Simulate some token usage for the test user
            const usage = await makeRequest('/api/simulate-usage', 'POST', {
                user_id: 'test_user',
                user_email: 'test@example.com',
                tokens: 500
            });
        }
        
        async function refreshData() {
            const data = await makeRequest('/api/admin/cost-dashboard');
            document.getElementById('liveData').innerHTML = 
                '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
        }
        
        // Auto-refresh every 30 seconds
        setInterval(refreshData, 30000);
        refreshData(); // Initial load
    </script>
</body>
</html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def send_cost_dashboard(self):
        """Send admin cost dashboard data"""
        user_email = self.headers.get('x-user-email', 'unknown@example.com')
        
        # Check admin permissions
        if not admin_role_manager.is_admin(user_email):
            self.send_json_response({
                'error': 'Admin access required',
                'user_email': user_email,
                'role': str(admin_role_manager.get_user_role(user_email))
            }, 403)
            return
        
        # Get system usage statistics
        system_usage = token_tracker.get_system_usage(30)
        budget_summary = budget_validator.get_budget_summary()
        top_users = token_tracker.get_top_users(5)
        
        response_data = {
            'dashboard_type': 'admin_cost_dashboard',
            'admin_user': user_email,
            'timestamp': datetime.utcnow().isoformat(),
            'system_usage': system_usage,
            'budget_summary': budget_summary,
            'top_users': top_users,
            'admin_privileges': True
        }
        
        self.send_json_response(response_data)
    
    def send_user_list(self):
        """Send list of users for admin"""
        user_email = self.headers.get('x-user-email', 'unknown@example.com')
        
        if not admin_role_manager.is_admin(user_email):
            self.send_json_response({'error': 'Admin access required'}, 403)
            return
        
        users = token_tracker.get_top_users(100)
        for user in users:
            user_id = user['user_id']
            user['budget_status'] = budget_validator.get_user_budget_status(user_id)
            user['is_blocked'] = user_id in budget_validator.blocked_users
        
        self.send_json_response({
            'users': users,
            'total_users': len(users),
            'blocked_users': len(budget_validator.blocked_users),
            'admin_user': user_email
        })
    
    def send_health_status(self):
        """Send system health status"""
        user_email = self.headers.get('x-user-email', 'unknown@example.com')
        
        if not admin_role_manager.is_admin(user_email):
            self.send_json_response({'error': 'Admin access required'}, 403)
            return
        
        system_usage = token_tracker.get_system_usage(7)
        budget_summary = budget_validator.get_budget_summary()
        
        health_score = 100
        if len(budget_validator.blocked_users) > 0:
            health_score -= len(budget_validator.blocked_users) * 10
        
        self.send_json_response({
            'health_score': health_score,
            'health_status': 'excellent' if health_score >= 90 else 'good',
            'system_metrics': {
                'total_users': system_usage['total_users'],
                'blocked_users': len(budget_validator.blocked_users),
                'total_requests_7d': system_usage['total_requests'],
                'total_cost_7d': system_usage['total_cost_usd']
            },
            'admin_user': user_email,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    def send_user_budget(self):
        """Send user's own budget status"""
        user_id = self.headers.get('x-user-id', 'test_user')
        user_email = self.headers.get('x-user-email', 'test@example.com')
        
        budget_status = budget_validator.get_user_budget_status(user_id)
        user_stats = token_tracker.get_user_usage(user_id)
        forecast = token_tracker.get_cost_forecast(user_id)
        
        self.send_json_response({
            'user_id': user_id,
            'user_email': user_email,
            'budget_status': budget_status,
            'usage_stats': user_stats.to_dict() if user_stats else None,
            'cost_forecast': forecast,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    def handle_spiritual_guidance(self, post_data):
        """Simulate spiritual guidance with token tracking"""
        try:
            data = json.loads(post_data.decode())
            user_id = self.headers.get('x-user-id', 'test_user')
            user_email = self.headers.get('x-user-email', 'test@example.com')
            session_id = self.headers.get('x-session-id', 'session_123')
            
            # Check budget first
            can_proceed, error = budget_validator.validate_request_budget(
                user_id, user_email, 0.15  # Estimated cost
            )
            
            if not can_proceed:
                self.send_json_response({
                    'response': f"🙏 {error}",
                    'budget_limited': True,
                    'error': error
                })
                return
            
            # Record token usage
            usage = token_tracker.record_usage(
                user_id=user_id,
                user_email=user_email,
                session_id=session_id,
                model='gemini-2.5-flash',
                input_tokens=len(data.get('query', '')) * 2,  # Rough estimate
                output_tokens=300,
                request_type='spiritual_guidance',
                response_quality='high'
            )
            
            # Send spiritual response
            self.send_json_response({
                'response': f"🕉️ Dear {user_email.split('@')[0]}, regarding '{data.get('query', '')}': The path of dharma teaches us that righteous action brings inner peace. As Krishna taught Arjuna, perform your duty without attachment to results.",
                'citations': ['Bhagavad Gita 2.47', 'Bhagavad Gita 3.8'],
                'metadata': {
                    'user_id': user_id,
                    'token_usage': {
                        'total_tokens': usage.total_tokens,
                        'cost_usd': usage.cost_usd
                    },
                    'budget_status': 'within_limits',
                    'timestamp': datetime.utcnow().isoformat()
                }
            })
            
        except Exception as e:
            self.send_error_response(str(e))
    
    def handle_user_block(self, path):
        """Handle user blocking"""
        user_email = self.headers.get('x-user-email', 'unknown@example.com')
        
        if not admin_role_manager.is_admin(user_email):
            self.send_json_response({'error': 'Admin access required'}, 403)
            return
        
        # Extract user_id from path
        user_id = path.split('/')[-2]  # /api/admin/users/{user_id}/block
        
        budget_validator.blocked_users.add(user_id)
        
        self.send_json_response({
            'message': f'User {user_id} blocked successfully',
            'action': 'block',
            'admin': user_email,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    def handle_user_unblock(self, path):
        """Handle user unblocking"""
        user_email = self.headers.get('x-user-email', 'unknown@example.com')
        
        if not admin_role_manager.is_admin(user_email):
            self.send_json_response({'error': 'Admin access required'}, 403)
            return
        
        # Extract user_id from path
        user_id = path.split('/')[-2]  # /api/admin/users/{user_id}/unblock
        
        success = budget_validator.unblock_user(user_id, user_email)
        
        self.send_json_response({
            'message': f'User {user_id} unblocked successfully' if success else 'User not blocked',
            'action': 'unblock',
            'success': success,
            'admin': user_email,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    def handle_budget_create(self, post_data):
        """Handle budget creation"""
        user_email = self.headers.get('x-user-email', 'unknown@example.com')
        
        if not admin_role_manager.is_admin(user_email):
            self.send_json_response({'error': 'Admin access required'}, 403)
            return
        
        try:
            data = json.loads(post_data.decode())
            budget = budget_validator.set_user_budget(
                user_id=data['user_id'],
                user_email=data['user_email'],
                monthly_limit=float(data.get('monthly_limit', 50.0))
            )
            
            self.send_json_response({
                'message': 'Budget created successfully',
                'budget': budget.to_dict(),
                'admin': user_email
            })
            
        except Exception as e:
            self.send_error_response(str(e))
    
    def send_json_response(self, data, status_code=200):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, x-user-email, x-user-id, x-session-id')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())
    
    def send_error_response(self, error):
        """Send error response"""
        self.send_json_response({
            'error': 'Internal server error',
            'message': error,
            'timestamp': datetime.utcnow().isoformat()
        }, 500)
    
    def send_404(self):
        """Send 404 response"""
        self.send_json_response({
            'error': 'Not found',
            'path': self.path
        }, 404)
    
    def log_message(self, format, *args):
        """Override log message to reduce noise"""
        logger.info(f"{self.address_string()} - {format % args}")


def start_test_server(port=8000):
    """Start the test server"""
    
    # Initialize some test data
    print("🔧 Initializing test data...")
    
    # Create test user budget
    budget_validator.set_user_budget(
        user_id='test_user',
        user_email='test@example.com',
        monthly_limit=50.0
    )
    
    # Record some test usage
    token_tracker.record_usage(
        user_id='test_user',
        user_email='test@example.com',
        session_id='session_123',
        model='gemini-2.5-flash',
        input_tokens=150,
        output_tokens=300,
        request_type='spiritual_guidance',
        response_quality='high'
    )
    
    # Create another test user
    budget_validator.set_user_budget(
        user_id='demo_user',
        user_email='demo@example.com',
        monthly_limit=25.0
    )
    
    token_tracker.record_usage(
        user_id='demo_user',
        user_email='demo@example.com',
        session_id='session_456',
        model='gemini-2.5-flash',
        input_tokens=200,
        output_tokens=400,
        request_type='spiritual_guidance',
        response_quality='high'
    )
    
    print(f"✅ Test data initialized")
    print(f"👑 Admin user: vedprakash.m@outlook.com")
    print(f"👤 Test users: test@example.com, demo@example.com")
    
    # Start server
    server = HTTPServer(('localhost', port), AdminTestHandler)
    print(f"\n🚀 Admin Features Test Server starting on http://localhost:{port}")
    print(f"📊 Open http://localhost:{port} in your browser to test admin features")
    print(f"🔐 Admin endpoints available at /api/admin/*")
    print(f"👤 User endpoints available at /api/user/*")
    print(f"\nPress Ctrl+C to stop the server")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print(f"\n🛑 Server stopped")
        server.server_close()


if __name__ == "__main__":
    start_test_server()
