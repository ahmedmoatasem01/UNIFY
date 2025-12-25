"""
Study Plan Service
AI-powered service for generating and managing personalized study plans
"""
from datetime import datetime, timedelta, date, time
from typing import List, Dict, Optional
import json
from models.study_plan import StudyPlan
from models.study_task import StudyTask
from models.study_recommendation import StudyRecommendation
from repositories.repository_factory import RepositoryFactory
from services.task_decomposition_service import TaskDecompositionService


class StudyPlanService:
    """Service for creating and managing AI-powered study plans"""
    
    def __init__(self):
        self.plan_repo = RepositoryFactory.get_repository('study_plan')
        self.task_repo = RepositoryFactory.get_repository('study_task')
        self.recommendation_repo = RepositoryFactory.get_repository('study_recommendation')
        self.decomposition_service = TaskDecompositionService()
        
    def generate_study_plan(self, student_id: int, course_id: Optional[int] = None,
                           plan_name: str = "", start_date: Optional[date] = None,
                           end_date: Optional[date] = None,
                           include_existing_tasks: bool = True) -> StudyPlan:
        """
        Generate a personalized study plan for a student
        
        Args:
            student_id: ID of the student
            course_id: Optional course ID to focus on
            plan_name: Name for the study plan
            start_date: Start date for the plan
            end_date: End date for the plan
            include_existing_tasks: Whether to include existing tasks
            
        Returns:
            Created StudyPlan object
        """
        # Set default dates if not provided
        if not start_date:
            start_date = date.today()
        if not end_date:
            end_date = start_date + timedelta(days=30)
        
        # Generate plan name if not provided
        if not plan_name:
            if course_id:
                course_repo = RepositoryFactory.get_repository('course')
                course = course_repo.get_by_id(course_id)
                plan_name = f"Study Plan for {course.Course_Name if course else 'Course'}"
            else:
                plan_name = f"Study Plan - {start_date.strftime('%B %Y')}"
        
        # Create the study plan
        plan = StudyPlan(
            Student_ID=student_id,
            Course_ID=course_id,
            Plan_Name=plan_name,
            Start_Date=start_date,
            End_Date=end_date,
            Status='active',
            Completion_Percentage=0.0
        )
        
        created_plan = self.plan_repo.create(plan)
        
        # Generate study tasks based on existing assignments and deadlines
        if include_existing_tasks:
            self._generate_tasks_from_assignments(created_plan, student_id, course_id)
        
        # Analyze student's productivity patterns and optimize schedule
        self._optimize_study_schedule(created_plan, student_id)
        
        return created_plan
    
    def _generate_tasks_from_assignments(self, plan: StudyPlan, student_id: int,
                                        course_id: Optional[int] = None):
        """Generate study tasks from existing assignments"""
        # Get existing tasks/assignments for the student
        task_repo = RepositoryFactory.get_repository('task')
        
        if course_id:
            # Get tasks for specific course (would need to add this query)
            existing_tasks = task_repo.get_by_student(student_id)
        else:
            existing_tasks = task_repo.get_by_student(student_id)
        
        # Filter tasks within the plan date range
        for task in existing_tasks:
            if task.Due_Date and plan.Start_Date <= task.Due_Date.date() <= plan.End_Date:
                # Create study task from assignment
                study_task = StudyTask(
                    Plan_ID=plan.Plan_ID,
                    Task_Title=f"Complete: {task.Task_Title}",
                    Description=f"Assignment task from course",
                    Due_Date=task.Due_Date,
                    Priority=task.Priority,
                    Status='pending'
                )
                
                # Estimate hours for the task
                estimated_hours = self.decomposition_service.estimate_task_duration(
                    task.Task_Title, ""
                )
                study_task.Estimated_Hours = estimated_hours
                
                # Create the study task
                created_task = self.task_repo.create(study_task)
                
                # Decompose if it's a large task
                if estimated_hours > 4.0:
                    self._decompose_and_create_subtasks(created_task, task.Task_Title, "")
    
    def _decompose_and_create_subtasks(self, parent_task: StudyTask, 
                                       title: str, description: str):
        """Decompose a task and create subtasks"""
        subtasks = self.decomposition_service.decompose_task(
            title,
            description,
            parent_task.Estimated_Hours or 5.0,
            parent_task.Due_Date or datetime.now() + timedelta(days=7)
        )
        
        for subtask_data in subtasks:
            subtask = StudyTask(
                Plan_ID=parent_task.Plan_ID,
                Parent_Task_ID=parent_task.Task_ID,
                Task_Title=subtask_data['title'],
                Description=subtask_data['description'],
                Estimated_Hours=subtask_data['estimated_hours'],
                Due_Date=subtask_data['due_date'],
                Priority=subtask_data['priority'],
                Status='pending'
            )
            self.task_repo.create(subtask)
    
    def _optimize_study_schedule(self, plan: StudyPlan, student_id: int):
        """Optimize study schedule based on student's productivity patterns"""
        # Get student's focus session history
        focus_repo = RepositoryFactory.get_repository('focus_session')
        focus_sessions = focus_repo.get_by_student(student_id)
        
        # Analyze productivity patterns
        productivity_data = self._analyze_productivity_patterns(focus_sessions)
        
        # Get all tasks for the plan
        tasks = self.task_repo.get_by_plan(plan.Plan_ID)
        
        # Distribute tasks across available time slots
        self._distribute_tasks_optimally(tasks, productivity_data, plan)
    
    def _analyze_productivity_patterns(self, focus_sessions: List) -> Dict:
        """Analyze student's productivity patterns from focus sessions"""
        if not focus_sessions:
            return {
                'peak_hours': [9, 10, 14, 15, 19, 20],  # Default productive hours
                'avg_session_duration': 25,  # minutes
                'completion_rate': 0.7
            }
        
        # Analyze by hour of day
        hourly_productivity = {}
        total_completed = 0
        total_sessions = len(focus_sessions)
        
        for session in focus_sessions:
            if session.Start_Time:
                hour = session.Start_Time.hour
                if hour not in hourly_productivity:
                    hourly_productivity[hour] = {'count': 0, 'completed': 0}
                hourly_productivity[hour]['count'] += 1
                if session.Completed:
                    hourly_productivity[hour]['completed'] += 1
                    total_completed += 1
        
        # Find peak hours (top 6 most productive hours)
        peak_hours = sorted(hourly_productivity.keys(), 
                          key=lambda h: hourly_productivity[h]['completed'] / max(hourly_productivity[h]['count'], 1),
                          reverse=True)[:6]
        
        # Calculate average session duration
        durations = [s.Duration for s in focus_sessions if s.Duration]
        avg_duration = sum(durations) / len(durations) if durations else 25
        
        return {
            'peak_hours': peak_hours if peak_hours else [9, 10, 14, 15, 19, 20],
            'avg_session_duration': avg_duration,
            'completion_rate': total_completed / total_sessions if total_sessions > 0 else 0.7
        }
    
    def _distribute_tasks_optimally(self, tasks: List[StudyTask], 
                                   productivity_data: Dict, plan: StudyPlan):
        """Distribute tasks optimally across the study plan period"""
        # This is a simplified version. In production, this would use
        # constraint satisfaction algorithms or optimization techniques
        
        # Sort tasks by priority and due date
        sorted_tasks = sorted(tasks, 
                            key=lambda t: (
                                {'high': 0, 'medium': 1, 'low': 2}.get(t.Priority, 1),
                                t.Due_Date or datetime.max
                            ))
        
        # The actual scheduling would be done here
        # For now, we just ensure tasks have proper priorities
        pass
    
    def adjust_study_plan(self, plan_id: int, reason: str = 'manual') -> StudyPlan:
        """
        Adjust study plan based on progress or changes
        
        Args:
            plan_id: ID of the study plan
            reason: Reason for adjustment ('manual', 'behind_schedule', 'deadline_change')
            
        Returns:
            Updated StudyPlan
        """
        plan = self.plan_repo.get_by_id(plan_id)
        if not plan:
            raise ValueError(f"Study plan {plan_id} not found")
        
        # Get all tasks for the plan
        tasks = self.task_repo.get_by_plan(plan_id)
        
        # Calculate current completion percentage
        completed_tasks = [t for t in tasks if t.Status == 'completed']
        if tasks:
            completion_pct = (len(completed_tasks) / len(tasks)) * 100
            plan.Completion_Percentage = completion_pct
        
        # Check if student is behind schedule
        pending_tasks = [t for t in tasks if t.Status == 'pending' and t.Due_Date]
        overdue_tasks = [t for t in pending_tasks if t.Due_Date < datetime.now()]
        
        if overdue_tasks:
            # Reschedule overdue tasks
            self._reschedule_overdue_tasks(overdue_tasks, plan)
        
        # Update the plan
        updated_plan = self.plan_repo.update(plan)
        
        return updated_plan
    
    def _reschedule_overdue_tasks(self, overdue_tasks: List[StudyTask], plan: StudyPlan):
        """Reschedule overdue tasks"""
        # Redistribute overdue tasks across remaining time
        days_remaining = (plan.End_Date - date.today()).days
        
        if days_remaining <= 0:
            # Extend plan if needed
            plan.End_Date = date.today() + timedelta(days=7)
            days_remaining = 7
        
        # Reschedule tasks evenly
        for i, task in enumerate(overdue_tasks):
            days_offset = (i + 1) * (days_remaining // max(len(overdue_tasks), 1))
            task.Due_Date = datetime.now() + timedelta(days=days_offset)
            task.Priority = 'high'  # Mark as high priority
            self.task_repo.update(task)
    
    def generate_recommendations(self, student_id: int, course_id: Optional[int] = None,
                                topic: Optional[str] = None) -> List[StudyRecommendation]:
        """
        Generate AI-powered study resource recommendations
        
        Args:
            student_id: ID of the student
            course_id: Optional course ID
            topic: Optional specific topic
            
        Returns:
            List of StudyRecommendation objects
        """
        recommendations = []
        
        # In production, this would use RAG (Retrieval-Augmented Generation)
        # to find relevant resources from the knowledge base
        
        # For now, create some example recommendations
        resource_types = ['note', 'video', 'practice', 'textbook']
        
        for i, res_type in enumerate(resource_types):
            rec = StudyRecommendation(
                Student_ID=student_id,
                Course_ID=course_id,
                Topic=topic or "General Study",
                Resource_Type=res_type,
                Resource_Link=f"/resources/{res_type}/{i}",
                Reason=f"Recommended based on your study patterns and course progress",
                Relevance_Score=0.85 - (i * 0.1)
            )
            created_rec = self.recommendation_repo.create(rec)
            recommendations.append(created_rec)
        
        return recommendations
    
    def get_study_plan_analytics(self, plan_id: int) -> Dict:
        """Get analytics for a study plan"""
        plan = self.plan_repo.get_by_id(plan_id)
        if not plan:
            return {}
        
        tasks = self.task_repo.get_by_plan(plan_id)
        
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t.Status == 'completed'])
        pending_tasks = len([t for t in tasks if t.Status == 'pending'])
        in_progress_tasks = len([t for t in tasks if t.Status == 'in_progress'])
        
        total_estimated_hours = sum(t.Estimated_Hours or 0 for t in tasks)
        total_actual_hours = sum(t.Actual_Hours or 0 for t in tasks)
        
        return {
            'plan_id': plan_id,
            'plan_name': plan.Plan_Name,
            'status': plan.Status,
            'completion_percentage': plan.Completion_Percentage,
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'pending_tasks': pending_tasks,
            'in_progress_tasks': in_progress_tasks,
            'total_estimated_hours': total_estimated_hours,
            'total_actual_hours': total_actual_hours,
            'efficiency': (total_actual_hours / total_estimated_hours * 100) if total_estimated_hours > 0 else 0
        }
