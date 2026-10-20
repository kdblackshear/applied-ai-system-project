from datetime import datetime, timedelta
from pawpal_system import Owner, OwnerPreferences, Pet, Task, Scheduler

def main():
    print("🐾 Initializing PawPal System...\n")

    # 1. Create Owner and Preferences
    preferences = OwnerPreferences(max_daily_minutes=240)
    owner = Owner(owner_id="o1", name="Sarah Connor", preferences=preferences)

    # 2. Initialize the Scheduler with the Owner
    scheduler = Scheduler(owner=owner)

    # 3. Create and Add Pets
    dog = Pet(
        pet_id="p1", 
        name="Buster", 
        type="Dog", 
        special_notes="High energy, needs morning exercise."
    )
    cat = Pet(
        pet_id="p2", 
        name="Luna", 
        type="Cat", 
        special_notes="Needs medication with evening meal."
    )

    scheduler.add_pet(dog)
    scheduler.add_pet(cat)
    print(f"Registered pets for {owner.name}: {dog.name} ({dog.type}), {cat.name} ({cat.type})\n")

    # 4. Add Tasks (Including an Overlapping Conflict Task)
    today = datetime.now()
    
    # Task 3: Evening Grooming
    groom_time = today.replace(hour=18, minute=0, second=0, microsecond=0)
    t3 = Task(
        task_id="t3",
        pet_id="p1",
        description="Coat brushing and dental check.",
        category="Grooming",
        duration_minutes=20,
        priority="Low",
        scheduled_time=groom_time,
        frequency="Weekly"
    )

    # Task 2: Breakfast/Feeding
    feed_time = today.replace(hour=9, minute=0, second=0, microsecond=0)
    t2 = Task(
        task_id="t2",
        pet_id="p2",
        description="Feed wet food and fresh water.",
        category="Feeding",
        duration_minutes=15,
        priority="Medium",
        scheduled_time=feed_time,
        frequency="Daily"
    )

    # Task 1: Morning Walk (8:30 AM - 9:15 AM)
    walk_time = today.replace(hour=8, minute=30, second=0, microsecond=0)
    t1 = Task(
        task_id="t1",
        pet_id="p1",
        description="Brisk 45-minute walk around the neighborhood park.",
        category="Walk",
        duration_minutes=45,
        priority="High",
        scheduled_time=walk_time,
        frequency="Daily"
    )

    # Task 4: Conflicting Task! (8:45 AM - Overlaps with Task 1)
    conflict_time = today.replace(hour=8, minute=45, second=0, microsecond=0)
    t4 = Task(
        task_id="t4",
        pet_id="p2",
        description="Urgent vet consultation call.",
        category="Medical",
        duration_minutes=30,
        priority="High",
        scheduled_time=conflict_time,
        frequency="Once"
    )

    print("=" * 60)
    print("⚠️ TESTING CONFLICT DETECTION DURING SCHEDULING")
    print("=" * 60)

    # Schedule tasks (t4 will trigger the overlap warning)
    scheduler.schedule_task(t3)
    scheduler.schedule_task(t2)
    scheduler.schedule_task(t1)
    scheduler.schedule_task(t4)
    
    print("\nSuccessfully processed all tasks.\n")

    # 5. Demonstrate sort_by_time() Method
    print("=" * 60)
    print("⏰ TESTING SORT_BY_TIME() METHOD (Chronological Order)")
    print("=" * 60)

    sorted_tasks = scheduler.sort_by_time()
    for i, task in enumerate(sorted_tasks, 1):
        time_str = task.scheduled_time.strftime("%I:%M %p")
        pet_obj = owner.pets.get(task.pet_id)
        print(f"{i}. [{time_str}] {task.description} - Pet: {pet_obj.name if pet_obj else 'Unknown'}")

    print("\n" + "=" * 60)
    print("📅 TODAY'S SCHEDULE & SMART PLAN")
    print("=" * 60)

    plan = scheduler.generate_daily_plan(today.date())
    print(f"\n💡 {plan['explanation']}\n")
    print("-" * 60)

    for i, task in enumerate(plan["schedule"], 1):
        pet_obj = owner.pets.get(task.pet_id)
        pet_name = pet_obj.name if pet_obj else "Unknown Pet"
        time_str = task.scheduled_time.strftime("%I:%M %p")
        
        print(f"{i}. [{task.priority.upper()}] {task.description} ({time_str})")
        print(   f"   • Pet: {pet_name}")
        print(   f"   • Category: {task.category} | Duration: {task.duration_minutes} mins")
        print("-" * 60)

if __name__ == "__main__":
    main()