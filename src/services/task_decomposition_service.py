"""
Task Decomposition Service
AI-powered service to break down complex assignments into manageable subtasks
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json
import os
from models.study_task import StudyTask


class TaskDecompositionService:
    """Service for decomposing complex tasks into subtasks using AI"""
    
    def __init__(self):
        self.default_task_duration = 2.0  # hours
        self.max_task_duration = 4.0  # hours
        
    def decompose_task(self, task_title: str, task_description: str, 
                       estimated_hours: float, due_date: datetime,
                       course_context: Optional[str] = None) -> List[Dict]:
        """
        Decompose a complex task into smaller subtasks
        
        Args:
            task_title: Title of the main task
            task_description: Description of the task
            estimated_hours: Total estimated hours
            due_date: Due date for the main task
            course_context: Optional course context for better decomposition
            
        Returns:
            List of subtask dictionaries
        """
        subtasks = []
        
        # Simple heuristic-based decomposition
        # In production, this would use an LLM API (e.g., OpenAI, Gemini)
        
        if estimated_hours <= self.max_task_duration:
            # Task is small enough, no decomposition needed
            return []
        
        # Determine number of subtasks based on estimated hours
        num_subtasks = max(2, min(int(estimated_hours / self.default_task_duration), 8))
        hours_per_subtask = estimated_hours / num_subtasks
        
        # Generate subtasks based on task type
        task_type = self._identify_task_type(task_title, task_description)
        subtask_templates = self._get_subtask_templates(task_type, num_subtasks)
        
        # Calculate time distribution
        days_until_due = (due_date - datetime.now()).days
        time_per_subtask = timedelta(days=max(1, days_until_due // num_subtasks))
        
        for i, template in enumerate(subtask_templates):
            subtask_due = due_date - timedelta(days=(num_subtasks - i - 1) * time_per_subtask.days)
            
            subtasks.append({
                'title': template['title'].format(main_task=task_title),
                'description': template['description'],
                'estimated_hours': hours_per_subtask,
                'due_date': subtask_due,
                'priority': template.get('priority', 'medium'),
                'order': i + 1
            })
        
        return subtasks
    
    def _identify_task_type(self, title: str, description: str) -> str:
        """Identify the type of task based on title and description"""
        text = (title + " " + (description or "")).lower()
        
        if any(word in text for word in ['essay', 'paper', 'report', 'write', 'writing']):
            return 'writing'
        elif any(word in text for word in ['project', 'implement', 'build', 'develop', 'code']):
            return 'project'
        elif any(word in text for word in ['study', 'exam', 'test', 'quiz', 'midterm', 'final']):
            return 'exam_prep'
        elif any(word in text for word in ['research', 'investigate', 'analyze', 'explore']):
            return 'research'
        elif any(word in text for word in ['presentation', 'present', 'slides']):
            return 'presentation'
        elif any(word in text for word in ['problem', 'homework', 'assignment', 'exercise']):
            return 'problem_set'
        else:
            return 'general'
    
    def _get_subtask_templates(self, task_type: str, num_subtasks: int) -> List[Dict]:
        """Get subtask templates based on task type"""
        templates = {
            'writing': [
                {'title': 'Research and outline for {main_task}', 'description': 'Gather sources and create detailed outline', 'priority': 'high'},
                {'title': 'Write first draft of {main_task}', 'description': 'Complete initial draft based on outline', 'priority': 'high'},
                {'title': 'Revise and edit {main_task}', 'description': 'Review, revise, and improve content', 'priority': 'medium'},
                {'title': 'Final proofreading of {main_task}', 'description': 'Check grammar, formatting, and citations', 'priority': 'medium'},
            ],
            'project': [
                {'title': 'Plan and design for {main_task}', 'description': 'Create project plan and design architecture', 'priority': 'high'},
                {'title': 'Implement core features of {main_task}', 'description': 'Build main functionality', 'priority': 'high'},
                {'title': 'Testing and debugging {main_task}', 'description': 'Test thoroughly and fix bugs', 'priority': 'high'},
                {'title': 'Documentation and finalization of {main_task}', 'description': 'Write documentation and polish', 'priority': 'medium'},
            ],
            'exam_prep': [
                {'title': 'Review lecture notes for {main_task}', 'description': 'Go through all lecture materials', 'priority': 'high'},
                {'title': 'Practice problems for {main_task}', 'description': 'Work through practice questions', 'priority': 'high'},
                {'title': 'Create study guide for {main_task}', 'description': 'Summarize key concepts and formulas', 'priority': 'medium'},
                {'title': 'Final review for {main_task}', 'description': 'Quick review of all materials', 'priority': 'medium'},
            ],
            'research': [
                {'title': 'Literature review for {main_task}', 'description': 'Find and review relevant sources', 'priority': 'high'},
                {'title': 'Data collection for {main_task}', 'description': 'Gather necessary data or information', 'priority': 'high'},
                {'title': 'Analysis for {main_task}', 'description': 'Analyze collected data', 'priority': 'high'},
                {'title': 'Compile findings for {main_task}', 'description': 'Organize and document results', 'priority': 'medium'},
            ],
            'presentation': [
                {'title': 'Content preparation for {main_task}', 'description': 'Research and organize content', 'priority': 'high'},
                {'title': 'Create slides for {main_task}', 'description': 'Design and build presentation slides', 'priority': 'high'},
                {'title': 'Practice presentation for {main_task}', 'description': 'Rehearse and time presentation', 'priority': 'medium'},
            ],
            'problem_set': [
                {'title': 'Review concepts for {main_task}', 'description': 'Review relevant theory and formulas', 'priority': 'medium'},
                {'title': 'Solve problems for {main_task}', 'description': 'Work through all problems', 'priority': 'high'},
                {'title': 'Check and verify {main_task}', 'description': 'Review solutions and verify answers', 'priority': 'medium'},
            ],
            'general': [
                {'title': 'Preparation for {main_task}', 'description': 'Gather materials and plan approach', 'priority': 'medium'},
                {'title': 'Execute {main_task}', 'description': 'Complete main work', 'priority': 'high'},
                {'title': 'Review and finalize {main_task}', 'description': 'Check work and make final adjustments', 'priority': 'medium'},
            ]
        }
        
        template_list = templates.get(task_type, templates['general'])
        
        # Adjust number of subtasks if needed
        if len(template_list) > num_subtasks:
            return template_list[:num_subtasks]
        elif len(template_list) < num_subtasks:
            # Duplicate some tasks if we need more
            while len(template_list) < num_subtasks:
                template_list.append(template_list[-1].copy())
        
        return template_list
    
    def estimate_task_duration(self, task_title: str, task_description: str,
                              historical_data: Optional[List[Dict]] = None) -> float:
        """
        Estimate task duration based on historical data and task characteristics
        
        Args:
            task_title: Title of the task
            task_description: Description of the task
            historical_data: Optional list of similar completed tasks with actual hours
            
        Returns:
            Estimated hours
        """
        # Base estimation on task type
        task_type = self._identify_task_type(task_title, task_description)
        
        base_estimates = {
            'writing': 8.0,
            'project': 12.0,
            'exam_prep': 10.0,
            'research': 10.0,
            'presentation': 6.0,
            'problem_set': 4.0,
            'general': 5.0
        }
        
        base_estimate = base_estimates.get(task_type, 5.0)
        
        # Adjust based on historical data if available
        if historical_data and len(historical_data) > 0:
            avg_actual = sum(task.get('actual_hours', 0) for task in historical_data) / len(historical_data)
            avg_estimated = sum(task.get('estimated_hours', 1) for task in historical_data) / len(historical_data)
            
            if avg_estimated > 0:
                # Calculate adjustment factor based on student's historical accuracy
                adjustment_factor = avg_actual / avg_estimated
                base_estimate *= adjustment_factor
        
        return round(base_estimate, 1)
    
    def suggest_task_priority(self, due_date: datetime, estimated_hours: float,
                             course_weight: float = 1.0) -> str:
        """
        Suggest priority level for a task
        
        Args:
            due_date: Task due date
            estimated_hours: Estimated hours to complete
            course_weight: Weight/importance of the course (0.0-1.0)
            
        Returns:
            Priority level: 'low', 'medium', or 'high'
        """
        days_until_due = (due_date - datetime.now()).days
        
        # Calculate urgency score
        if days_until_due <= 0:
            return 'high'
        
        hours_per_day_needed = estimated_hours / max(days_until_due, 1)
        
        # High priority: needs >3 hours/day or due within 3 days
        if hours_per_day_needed > 3 or days_until_due <= 3:
            return 'high'
        # Medium priority: needs 1-3 hours/day or due within 7 days
        elif hours_per_day_needed > 1 or days_until_due <= 7:
            return 'medium'
        # Low priority: everything else
        else:
            return 'low'
