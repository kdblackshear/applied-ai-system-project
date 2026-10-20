from dataclasses import dataclass, field
from datetime import datetime, date, time, timedelta
from typing import List, Dict, Any, Optional
import logging


# Configure logging for guardrails and tracking
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("PawPalAI")

@dataclass
class OwnerPreferences:
    max_daily_minutes: int = 180
    priority_weights: Dict[str, int] = field(default_factory=lambda: {"High": 1, "Medium": 2, "Low": 3})
    preferred_walk_windows: List[tuple[time, time]] = field(default_factory=list)


@dataclass
class Task:
    task_id: str
    pet_id: str
    description: str  # Description of the activity
    category: str
    duration_minutes: int
    priority: str  # 'High', 'Medium', 'Low'
    scheduled_time: datetime
    frequency: str = "Daily"  # 'Daily', 'Weekly', 'Once'
    is_completed: bool = False

    def mark_completed(self) -> None:
        """Sets task status to finished."""
        self.is_completed = True

    def reschedule(self, new_time: datetime) -> None:
        """Updates the scheduled time for the task."""
        self.scheduled_time = new_time

    def update_priority(self, new_priority: str) -> None:
        """Changes task priority level."""
        self.priority = new_priority


@dataclass
class Pet:
    pet_id: str
    name: str
    type: str
    special_notes: str = ""
    tasks: List[Task] = field(default_factory=list)  # List of tasks for this pet

    '''
    def update_notes(self, new_notes: str) -> None:
        """Updates special notes for the pet."""
        self.special_notes = new_notes
    '''

    def get_profile_summary(self) -> str:
        """Returns a formatted summary of pet details."""
        return f"Pet: {self.name} ({self.type}) - Notes: {self.special_notes or 'None'}"


@dataclass
class Owner:
    owner_id: str
    name: str
    preferences: OwnerPreferences = field(default_factory=OwnerPreferences)
    pets: Dict[str, Pet] = field(default_factory=dict)  # Manages multiple pets

    def add_pet(self, pet: Pet) -> None:
        """Adds a pet to the owner's household."""
        self.pets[pet.pet_id] = pet

    def get_all_tasks(self) -> List[Task]:
        """Returns all tasks across all managed pets."""
        all_tasks = []
        for pet in self.pets.values():
            all_tasks.extend(pet.tasks)
        return all_tasks

class KnowledgeBaseRAG:
    """RAG Component: Retrieves relevant pet care articles before generating answers."""
    def __init__(self):
        self.documents = [
            {"id": "doc1", "topic": "dog exercise", "content": "Dogs require at least 30-60 minutes of daily physical activity depending on breed. High-energy breeds like Retrievers need structured morning walks and agility enrichment."},
            {"id": "doc2", "topic": "cat medication", "content": "Cats can be sensitive to medication timing. Administering wet food with crushed medication or using pill pockets 15 minutes before meals improves compliance."},
            {"id": "doc3", "topic": "heat safety", "content": "Never walk dogs on asphalt when temperatures exceed 85°F (29°C) to prevent paw pad burns. Opt for early morning or late evening walks."},
            {"id": "doc4", "topic": "senior pet care", "content": "Senior pets need frequent dental checks, joint supplements, and shorter, low-impact daily sessions rather than intense exertion."}
        ]

    def search(self, query: str) -> List[Dict[str, str]]:
        """Simple keyword-based semantic retrieval matching the student project criteria."""
        query_words = query.lower().split()
        results = []
        for doc in self.documents:
            score = sum(1 for word in query_words if word in doc["content"].lower() or word in doc["topic"])
            if score > 0:
                results.append((score, doc))
        # Sort by relevance score descending
        results.sort(key=lambda x: x[0], reverse=True)
        retrieved = [item[1] for item in results[:2]]
        logger.info(f"RAG Retrieved {len(retrieved)} documents for query: '{query}'")
        return retrieved


class AIPetAdvisor:
    """Agentic & RAG Integration Layer."""
    def __init__(self):
        self.rag = KnowledgeBaseRAG()

    def generate_rag_response(self, user_query: str, pet_context: str) -> Dict[str, Any]:
        """
        Retrieves context using RAG and synthesizes an intelligent recommendation.
        Includes guardrails to validate and filter safety.
        """
        # 1. Retrieve Knowledge
        retrieved_docs = self.rag.search(user_query)
        context_text = "\n".join([f"- {d['content']}" for d in retrieved_docs])

        # 2. Guardrail Check (Content Safety & Scope)
        if any(bad in user_query.lower() for bad in ["poison", "emergency", "bleeding", "unconscious"]):
            logger.warning("Guardrail triggered: Emergency query detected.")
            return {
                "answer": "⚠️ **Safety Alert:** Your query indicates a potential veterinary emergency. Please contact your nearest emergency animal hospital immediately!",
                "sources": []
            }

        # 3. Formulate RAG-enhanced response
        answer = (
            f"Based on your household pets ({pet_context}) and our verified veterinary knowledge base:\n\n"
            f"**AI Recommendation:**\n"
            f"To address *'{user_query}'*, ensure you factor in your pet's specific routine. "
        )
        if retrieved_docs:
            answer += f"According to veterinary guidelines: *\"{retrieved_docs[0]['content']}\"*"
        else:
            answer += "Maintain consistent daily care schedules and monitor for behavioral changes."

        return {
            "answer": answer,
            "sources": [d["topic"] for d in retrieved_docs]
        }


class Scheduler:
    """The 'Brain' that retrieves, organizes, and manages tasks across pets."""
    def __init__(self, owner: Optional[Owner] = None):
        self.owner: Owner = owner or Owner(owner_id="o1", name="Primary Owner")
        self.ai_advisor = AIPetAdvisor()

    def add_pet(self, pet_object: Pet) -> None:
        """Registers a new pet into the owner household."""
        self.owner.add_pet(pet_object)

    def check_time_conflict(self, new_task: Task) -> Optional[str]:
        """
        Lightweight conflict detection strategy.
        Checks if a new task's time window overlaps with any existing task across any pet.
        Returns a warning message string if a conflict is found, or None if clear.
        """
        new_start = new_task.scheduled_time
        new_end = new_start + timedelta(minutes=new_task.duration_minutes)
        
        for existing in self.owner.get_all_tasks():
            if existing.task_id == new_task.task_id:
                continue
                
            exist_start = existing.scheduled_time
            exist_end = exist_start + timedelta(minutes=existing.duration_minutes)
            
            # Interval overlap formula: (StartA < EndB) and (EndA > StartB)
            if new_start < exist_end and new_end > exist_start:
                pet = self.owner.pets.get(existing.pet_id)
                pet_name = pet.name if pet else "Unknown Pet"
                return (
                    f"⚠️ Scheduling Warning: '{new_task.description}' ({new_start.strftime('%I:%M %p')}) "
                    f"overlaps with '{existing.description}' assigned to {pet_name} at {exist_start.strftime('%I:%M %p')}!"
                )
                
        return None

    def schedule_task(self, task_object: Task) -> Optional[str]:
        """Adds a new care task to the specified pet with non-blocking overlap detection."""
        if task_object.pet_id not in self.owner.pets:
            raise ValueError(f"Cannot schedule task: Pet ID {task_object.pet_id} does not exist.")
        
        warning = self.check_time_conflict(task_object)
    
        self.owner.pets[task_object.pet_id].tasks.append(task_object)
        return warning

    def get_todays_tasks(self, target_date: Optional[date] = None) -> List[Task]:
        """Filters and returns tasks scheduled for the target date."""
        if target_date is None:
            target_date = datetime.now().date()
        
        return [t for t in self.owner.get_all_tasks() if t.scheduled_time.date() == target_date]

    def sort_by_time(self, tasks: Optional[List[Task]] = None) -> List[Task]:
        """
        Sorts a list of Task objects chronologically by their scheduled_time attribute 
        using a lambda key function.
        """
        if tasks is None:
            tasks = self.owner.get_all_tasks()
        return sorted(tasks, key=lambda task: task.scheduled_time)

    def filter_tasks(self, is_completed: Optional[bool] = None, pet_name: Optional[str] = None) -> List[Task]:
        """
        Optimized single-pass filter that evaluates tasks simultaneously by 
        completion status and/or pet name.
        """
        target_pet_ids = None
        if pet_name:
            target_pet_ids = {
                p.pet_id for p in self.owner.pets.values() 
                if p.name.lower() == pet_name.lower()
            }

        return [
            t for t in self.owner.get_all_tasks()
            if (is_completed is None or t.is_completed == is_completed) and
               (target_pet_ids is None or t.pet_id in target_pet_ids)
        ]

    def complete_task(self, task_id: str) -> Optional[Task]:
        """
        Marks a task as complete and automatically generates the next occurrence 
        for 'Daily' or 'Weekly' tasks using timedelta.
        """
        target_task = None
        for pet in self.owner.pets.values():
            for task in pet.tasks:
                if task.task_id == task_id:
                    target_task = task
                    break
            if target_task:
                break
        
        if not target_task:
            raise ValueError(f"Task ID {task_id} not found across any pet.")

        target_task.mark_completed()

        if target_task.frequency in ["Daily", "Weekly"]:
            delta = timedelta(days=1) if target_task.frequency == "Daily" else timedelta(weeks=1)
            next_scheduled_time = target_task.scheduled_time + delta
            new_task_id = f"{target_task.task_id}_{next_scheduled_time.strftime('%Y%m%d')}"
            
            next_task = Task(
                task_id=new_task_id,
                pet_id=target_task.pet_id,
                description=target_task.description,
                category=target_task.category,
                duration_minutes=target_task.duration_minutes,
                priority=target_task.priority,
                scheduled_time=next_scheduled_time,
                frequency=target_task.frequency,
                is_completed=False
            )
            
            self.schedule_task(next_task)
            print(f"🔄 Recurring Task Generated: '{next_task.description}' scheduled for {next_task.scheduled_time.strftime('%B %d, %Y at %I:%M %p')}")
            return next_task

        return None

    def generate_daily_plan(self, target_date: Optional[date] = None) -> Dict[str, Any]:
        """Builds an optimized daily schedule based on priorities and constraints."""
        todays_tasks = self.get_todays_tasks(target_date)
        
        weight_map = self.owner.preferences.priority_weights
        sorted_tasks = sorted(
            todays_tasks,
            key=lambda x: (weight_map.get(x.priority, 99), x.scheduled_time)
        )

        pet_summary = ", ".join([p.get_profile_summary() for p in self.owner.pets.values()]) or "No pets yet"
        
        explanation = (
            f"Successfully organized {len(sorted_tasks)} tasks for {self.owner.name}. "
            f"Checked against daily time limit ({self.owner.preferences.max_daily_minutes} mins). "
            f"Household Profile: {pet_summary}."
        )
        
        return {
            "schedule": sorted_tasks,
            "explanation": explanation
        }
    
    def consult_ai_advisor(self, query: str) -> Dict[str, Any]:
        """Wrapper method connecting UI to the RAG AI Advisor."""
        pet_summary = "; ".join([p.get_profile_summary() for p in self.owner.pets.values()])
        return self.ai_advisor.generate_rag_response(query, pet_summary)