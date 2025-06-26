"""
Azure Functions endpoints for Vimarsh Feedback Collection API
Handles feedback collection, analysis, and reporting with Azure Function bindings
"""

import json
import logging
import os
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import azure.functions as func
from azure.functions import HttpRequest, HttpResponse

# Import our feedback collector
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from feedback.vimarsh_feedback_collector import (
        VimarshFeedbackCollector, 
        FeedbackType, 
        collect_user_feedback,
        generate_weekly_feedback_report
    )
except ImportError:
    logging.error("Failed to import feedback collector")
    # Fallback implementation
    class VimarshFeedbackCollector:
        async def collect_feedback(self, **kwargs):
            return "feedback_id_placeholder"
        
        async def analyze_feedback_trends(self, days=7):
            return {}
        
        async def generate_feedback_report(self, days=7):
            return {}

async def collect_feedback_endpoint(req: HttpRequest) -> HttpResponse:
    """
    Collect user feedback - supports both JSON and multipart (for voice feedback)
    POST /api/feedback/collect
    """
    try:
        # Check content type
        content_type = req.headers.get('content-type', '')
        
        if 'multipart/form-data' in content_type:
            # Handle voice feedback with file upload
            feedback_data_str = req.form.get('feedback')
            if not feedback_data_str:
                return HttpResponse(
                    json.dumps({"error": "Missing feedback data"}),
                    status_code=400,
                    mimetype="application/json"
                )
            
            feedback_data = json.loads(feedback_data_str)
            
            # Handle audio file if present
            audio_file = req.files.get('audio')
            if audio_file:
                # Save audio file temporarily for processing
                audio_path = f"/tmp/feedback_audio_{datetime.now().timestamp()}.wav"
                with open(audio_path, 'wb') as f:
                    f.write(audio_file.read())
                
                # Add audio path to feedback data for processing
                feedback_data['audio_file_path'] = audio_path
        else:
            # Handle JSON feedback
            try:
                feedback_data = req.get_json()
            except ValueError:
                return HttpResponse(
                    json.dumps({"error": "Invalid JSON in request body"}),
                    status_code=400,
                    mimetype="application/json"
                )
        
        if not feedback_data:
            return HttpResponse(
                json.dumps({"error": "No feedback data provided"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Extract and validate feedback data
        feedback_type_str = feedback_data.get('feedback_type', 'text_feedback')
        try:
            feedback_type = FeedbackType(feedback_type_str)
        except ValueError:
            feedback_type = FeedbackType.TEXT_FEEDBACK
        
        user_id = feedback_data.get('user_id', 'anonymous')
        session_id = feedback_data.get('session_id', f"session_{datetime.now().timestamp()}")
        rating = feedback_data.get('rating')
        text_content = feedback_data.get('text_content')
        context = feedback_data.get('context', {})
        
        # Add request metadata to context
        context.update({
            'user_agent': req.headers.get('user-agent', ''),
            'timestamp': datetime.now().isoformat(),
            'ip_address': req.headers.get('x-forwarded-for', 'unknown')
        })
        
        # Collect feedback using our service
        feedback_id = await collect_user_feedback(
            user_id=user_id,
            session_id=session_id,
            feedback_type=feedback_type_str,
            rating=rating,
            text_content=text_content,
            context=context
        )
        
        # Clean up temporary audio file if it exists
        if 'audio_file_path' in feedback_data:
            try:
                os.remove(feedback_data['audio_file_path'])
            except:
                pass
        
        return HttpResponse(
            json.dumps({
                "success": True,
                "feedback_id": feedback_id,
                "message": "Feedback received successfully"
            }),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f"Error collecting feedback: {str(e)}")
        return HttpResponse(
            json.dumps({
                "error": "Failed to collect feedback",
                "message": str(e)
            }),
            status_code=500,
            mimetype="application/json"
        )

async def get_feedback_analytics(req: HttpRequest) -> HttpResponse:
    """
    Get feedback analytics for specified time period
    GET /api/feedback/analytics?days=7
    """
    try:
        # Parse query parameters
        days = int(req.params.get('days', '7'))
        
        if days < 1 or days > 365:
            return HttpResponse(
                json.dumps({"error": "Days must be between 1 and 365"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Get analytics
        collector = VimarshFeedbackCollector()
        analytics = await collector.analyze_feedback_trends(days)
        
        # Convert to serializable format
        if hasattr(analytics, '__dict__'):
            analytics_dict = analytics.__dict__
        else:
            analytics_dict = analytics
        
        return HttpResponse(
            json.dumps(analytics_dict, default=str),
            status_code=200,
            mimetype="application/json"
        )
        
    except ValueError as e:
        return HttpResponse(
            json.dumps({"error": f"Invalid parameter: {str(e)}"}),
            status_code=400,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Error getting feedback analytics: {str(e)}")
        return HttpResponse(
            json.dumps({
                "error": "Failed to get analytics",
                "message": str(e)
            }),
            status_code=500,
            mimetype="application/json"
        )

async def get_improvement_metrics(req: HttpRequest) -> HttpResponse:
    """
    Get continuous improvement metrics
    GET /api/feedback/improvement-metrics?days=7
    """
    try:
        days = int(req.params.get('days', '7'))
        
        if days < 1 or days > 365:
            return HttpResponse(
                json.dumps({"error": "Days must be between 1 and 365"}),
                status_code=400,
                mimetype="application/json"
            )
        
        collector = VimarshFeedbackCollector()
        metrics = await collector.generate_improvement_metrics(days)
        
        # Convert to serializable format
        if hasattr(metrics, '__dict__'):
            metrics_dict = metrics.__dict__
        else:
            metrics_dict = metrics
        
        return HttpResponse(
            json.dumps(metrics_dict, default=str),
            status_code=200,
            mimetype="application/json"
        )
        
    except ValueError as e:
        return HttpResponse(
            json.dumps({"error": f"Invalid parameter: {str(e)}"}),
            status_code=400,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Error getting improvement metrics: {str(e)}")
        return HttpResponse(
            json.dumps({
                "error": "Failed to get improvement metrics",
                "message": str(e)
            }),
            status_code=500,
            mimetype="application/json"
        )

async def export_feedback_report(req: HttpRequest) -> HttpResponse:
    """
    Export comprehensive feedback report
    GET /api/feedback/export-report?days=7&format=json
    """
    try:
        days = int(req.params.get('days', '7'))
        format_type = req.params.get('format', 'json').lower()
        
        if days < 1 or days > 365:
            return HttpResponse(
                json.dumps({"error": "Days must be between 1 and 365"}),
                status_code=400,
                mimetype="application/json"
            )
        
        if format_type not in ['json', 'csv']:
            return HttpResponse(
                json.dumps({"error": "Format must be 'json' or 'csv'"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Generate comprehensive report
        report = await generate_weekly_feedback_report()
        
        if format_type == 'json':
            return HttpResponse(
                json.dumps(report, default=str, indent=2),
                status_code=200,
                mimetype="application/json",
                headers={
                    'Content-Disposition': f'attachment; filename="feedback_report_{days}days.json"'
                }
            )
        else:
            # Convert to CSV (simplified version)
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow(['Metric', 'Value'])
            
            # Write data
            for key, value in report.items():
                if isinstance(value, (str, int, float)):
                    writer.writerow([key, value])
                elif isinstance(value, list):
                    writer.writerow([key, ', '.join(map(str, value))])
                elif isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        writer.writerow([f"{key}_{sub_key}", sub_value])
            
            csv_content = output.getvalue()
            output.close()
            
            return HttpResponse(
                csv_content,
                status_code=200,
                mimetype="text/csv",
                headers={
                    'Content-Disposition': f'attachment; filename="feedback_report_{days}days.csv"'
                }
            )
        
    except ValueError as e:
        return HttpResponse(
            json.dumps({"error": f"Invalid parameter: {str(e)}"}),
            status_code=400,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Error exporting feedback report: {str(e)}")
        return HttpResponse(
            json.dumps({
                "error": "Failed to export report",
                "message": str(e)
            }),
            status_code=500,
            mimetype="application/json"
        )

# Azure Function app configuration
app = func.FunctionApp()

@app.route(route="feedback/collect", methods=["POST"])
async def feedback_collect(req: HttpRequest) -> HttpResponse:
    """Collect user feedback endpoint"""
    return await collect_feedback_endpoint(req)

@app.route(route="feedback/analytics", methods=["GET"])
async def feedback_analytics(req: HttpRequest) -> HttpResponse:
    """Get feedback analytics endpoint"""
    return await get_feedback_analytics(req)

@app.route(route="feedback/improvement-metrics", methods=["GET"]) 
async def improvement_metrics(req: HttpRequest) -> HttpResponse:
    """Get improvement metrics endpoint"""
    return await get_improvement_metrics(req)

@app.route(route="feedback/export-report", methods=["GET"])
async def export_report(req: HttpRequest) -> HttpResponse:
    """Export feedback report endpoint"""
    return await export_feedback_report(req)

@app.route(route="feedback/health", methods=["GET"])
async def feedback_health(req: HttpRequest) -> HttpResponse:
    """Health check for feedback service"""
    return HttpResponse(
        json.dumps({
            "status": "healthy",
            "service": "vimarsh-feedback-api",
            "timestamp": datetime.now().isoformat()
        }),
        status_code=200,
        mimetype="application/json"
    )
