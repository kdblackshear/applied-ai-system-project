import pytest
from datetime import datetime, timedelta
from pawpal_system import Owner, OwnerPreferences, Pet, Task, Scheduler, KnowledgeBaseRAG, AIPetAdvisor

@pytest.fixture
def sample_scheduler():
    """Fixture to set up a clean scheduler instance with a pre-registered owner and pets."""
    preferences = OwnerPreferences(max_daily_minutes=180)
    owner = Owner(owner_id="o1", name="Sarah Connor", preferences=preferences)
    scheduler = Scheduler(owner=owner)
    
    dog = Pet(pet_id="p1", name="Buster", type="Dog", special_notes="High energy, morning exercise.")
    cat = Pet(pet_id="p2", name="Luna", type="Cat", special_notes="Medication with meals.")
    
    scheduler.add_pet(dog)
    scheduler.add_pet(cat)
    return scheduler

def test_add_pet_and_owner(sample_scheduler):
    """Test that pets and owners are initialized correctly."""
    assert len(sample_scheduler.owner.pets) == 2
    assert sample_scheduler.owner.name == "Sarah Connor"
    assert sample_scheduler.owner.pets["p1"].name == "Buster"
    assert sample_scheduler.owner.pets["p2"].type == "Cat"

def test_schedule_task_and_conflict_detection(sample_scheduler):
    """Test task scheduling and overlap/conflict warning detection."""
    today = datetime.now()
    
    # Task 1: 8:30 AM - 9:15 AM
    t1_time = today.replace(hour=8, minute=30, second=0, microsecond=0)
    t1 = Task(
        task_id="t1", pet_id="p1", description="Morning walk", category="Walk",
        duration_minutes=45, priority="High", scheduled_time=t1_time
    )
    warning1 = sample_scheduler.schedule_task(t1)
    assert warning1 is None  # First task should have no conflicts

    # Task 2: 8:45 AM (Overlaps with Task 1)
    t2_time = today.replace(hour=8, minute=45, second=0, microsecond=0)
    t2 = Task(
        task_id="t2", pet_id="p2", description="Vet consultation call", category="Medical",
        duration_minutes=30, priority="High", scheduled_time=t2_time
    )
    warning2 = sample_scheduler.schedule_task(t2)
    assert warning2 is not None
    assert "overlaps with" in warning2

def test_sort_and_filter_tasks(sample_scheduler):
    """Test chronological sorting and single-pass multi-criteria task filtering."""
    today = datetime.now()
    t_early = Task("t_early", "p1", "Early feeding", "Feeding", 15, "Medium", today.replace(hour=7, minute=0))
    t_late = Task("t_late", "p2", "Late grooming", "Grooming", 20, "Low", today.replace(hour=20, minute=0))
    
    sample_scheduler.schedule_task(t_early)
    sample_scheduler.schedule_task(t_late)

    # Test chronological sort
    sorted_tasks = sample_scheduler.sort_by_time()
    assert sorted_tasks[0].task_id == "t_early"
    assert sorted_tasks[1].task_id == "t_late"

    # Test pet-specific filtering
    filtered_buster = sample_scheduler.filter_tasks(pet_name="Buster")
    assert len(filtered_buster) == 1
    assert filtered_buster[0].pet_id == "p1"

def test_complete_task_recurring_generation(sample_scheduler):
    """Test completing a task automatically generates the next recurring occurrence."""
    today = datetime.now()
    t_daily = Task(
        task_id="t_daily", pet_id="p1", description="Daily walk", category="Walk",
        duration_minutes=30, priority="High", scheduled_time=today.replace(hour=10, minute=0), frequency="Daily"
    )
    sample_scheduler.schedule_task(t_daily)

    next_task = sample_scheduler.complete_task("t_daily")
    assert next_task is not None
    assert next_task.frequency == "Daily"
    assert next_task.scheduled_time.date() == (today + timedelta(days=1)).date()
    assert next_task.is_completed is False

def test_rag_knowledge_base_retrieval():
    """Test that the RAG retriever successfully queries and fetches relevant documents."""
    rag = KnowledgeBaseRAG()
    results = rag.search("dog exercise requirements")
    assert len(results) > 0
    assert any("dog exercise" in doc["topic"] for doc in results)

def test_ai_advisor_safety_guardrail():
    """Test that emergency keywords trigger safety guardrails instead of standard RAG advice."""
    advisor = AIPetAdvisor()
    res = advisor.generate_rag_response("My cat ingested poison and is bleeding", "Cat: Luna")
    assert "Safety Alert" in res["answer"]
    assert len(res["sources"]) == 0

def test_ai_advisor_rag_synthesis():
    """Test normal RAG query generation and source tracking."""
    advisor = AIPetAdvisor()
    res = advisor.generate_rag_response("How long should I walk my dog?", "Dog: Buster")
    assert "Based on your household pets" in res["answer"]
    assert len(res["sources"]) > 0

def test_generate_daily_plan(sample_scheduler):
    """Test optimized daily plan generation and explanation formatting."""
    today = datetime.now()
    t = Task("t_plan", "p1", "Walk", "Walk", 30, "High", today.replace(hour=9, minute=0))
    sample_scheduler.schedule_task(t)

    plan = sample_scheduler.generate_daily_plan()
    assert "schedule" in plan
    assert "explanation" in plan
    assert len(plan["schedule"]) == 1
    assert "Sarah Connor" in plan["explanation"]