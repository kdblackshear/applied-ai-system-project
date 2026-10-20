import streamlit as st
from datetime import datetime
from pawpal_system import Owner, OwnerPreferences, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

# --- Initialize Session State Backend ---
if "scheduler" not in st.session_state:
    default_owner = Owner(owner_id="o1", name="Jordan", preferences=OwnerPreferences(max_daily_minutes=180))
    st.session_state.scheduler = Scheduler(owner=default_owner)

scheduler = st.session_state.scheduler

st.markdown(
    """
Welcome to the PawPal+ pet care planning assistant. 
Manage your household, track tasks with priority constraints, and generate optimized daily plans!
"""
)

# --- Sidebar / Household Setup ---
with st.sidebar:
    st.header("🏠 Household Setup")
    
    current_owner_name = st.text_input("Owner Name", value=scheduler.owner.name)
    if current_owner_name != scheduler.owner.name:
        scheduler.owner.name = current_owner_name
        
    st.divider()
    
    st.subheader("Add a Pet")
    new_pet_id = st.text_input("Pet ID (e.g., p1)", value=f"p{len(scheduler.owner.pets) + 1}")
    new_pet_name = st.text_input("Pet Name", value="Mochi")
    new_species = st.selectbox("Species", ["dog", "cat", "other"])
    new_notes = st.text_area("Special Notes", value="")
    
    if st.button("Register Pet"):
        if new_pet_id and new_pet_name:
            try:
                pet_obj = Pet(pet_id=new_pet_id, name=new_pet_name, type=new_species, special_notes=new_notes)
                scheduler.add_pet(pet_obj)
                st.success(f"Successfully added {new_pet_name}!")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("Please provide both a Pet ID and Name.")

    st.divider()
    st.subheader("Registered Pets")
    if scheduler.owner.pets:
        for p_id, p_obj in scheduler.owner.pets.items():
            st.markdown(f"• **{p_obj.name}** ({p_obj.type})")
    else:
        st.info("No pets registered yet.")


st.divider()

# --- Main App Inputs: Quick Task Creator ---
st.subheader("Quick Task Creator")
st.caption("Add tasks to your registered pets to feed into the smart scheduler.")

if not scheduler.owner.pets:
    st.warning("⚠️ Please register at least one pet in the sidebar before adding tasks.")
else:
    with st.form("task_creation_form"):
        col1, col2 = st.columns(2)
        with col1:
            pet_choices = {p.name: p.pet_id for p in scheduler.owner.pets.values()}
            selected_pet_name = st.selectbox("Assign to Pet", list(pet_choices.keys()))
            target_pet_id = pet_choices[selected_pet_name]
            
            task_id = st.text_input("Task ID", value=f"t{len(scheduler.owner.get_all_tasks()) + 1}")
            task_description = st.text_input("Task Description", value="Morning walk")
            
        with col2:
            category = st.selectbox("Category", ["Walk", "Feeding", "Meds", "Grooming", "Enrichment"])
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
            priority = st.selectbox("Priority", ["High", "Medium", "Low"], index=2)
            scheduled_time = st.time_input("Scheduled Time", value=datetime.now().time())
            
        submitted_task = st.form_submit_button("Add Task")
        
        if submitted_task:
            if task_id and task_description:
                # Combine today's date with the selected time
                task_datetime = datetime.combine(datetime.now().date(), scheduled_time)
                new_task = Task(
                    task_id=task_id,
                    pet_id=target_pet_id,
                    description=task_description,
                    category=category,
                    duration_minutes=int(duration),
                    priority=priority,
                    scheduled_time=task_datetime
                )
                try:
                    # Capture warning from scheduler.schedule_task
                    warning_msg = scheduler.schedule_task(new_task)
                    if warning_msg:
                        st.warning(warning_msg)
                    st.success(f"Successfully added task for {selected_pet_name}!")
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.warning("Please provide a Task ID and Description.")

st.divider()

# --- Filter & Display Household Tasks using Scheduler methods ---
st.subheader("📋 Current Household Tasks")

all_tasks = scheduler.owner.get_all_tasks()
if all_tasks:
    # Optional filtering controls
    f_col1, f_col2 = st.columns(2)
    with f_col1:
        filter_status = st.selectbox("Filter by Status", ["All", "Pending", "Completed"])
    with f_col2:
        pet_filter_options = ["All"] + [p.name for p in scheduler.owner.pets.values()]
        filter_pet = st.selectbox("Filter by Pet", pet_filter_options)
        
    # Translate UI filters to parameters for scheduler.filter_tasks()
    status_bool = None
    if filter_status == "Pending":
        status_bool = False
    elif filter_status == "Completed":
        status_bool = True
        
    pet_name_arg = filter_pet if filter_pet != "All" else None
    
    # Use Scheduler filter and sort methods
    filtered_tasks = scheduler.filter_tasks(is_completed=status_bool, pet_name=pet_name_arg)
    sorted_tasks = scheduler.sort_by_time(filtered_tasks)
    
    if sorted_tasks:
        task_data = []
        for t in sorted_tasks:
            pet_name = scheduler.owner.pets[t.pet_id].name if t.pet_id in scheduler.owner.pets else "Unknown"
            task_data.append({
                "Time": t.scheduled_time.strftime("%I:%M %p"),
                "Pet": pet_name,
                "Description": t.description,
                "Category": t.category,
                "Duration": f"{t.duration_minutes}m",
                "Priority": t.priority,
                "Status": "Completed" if t.is_completed else "Pending"
            })
        st.table(task_data)
    else:
        st.info("No tasks match the selected filter criteria.")
else:
    st.info("No tasks created yet.")

st.divider()

# --- Build Schedule Integration ---
st.subheader("⚡ Build Optimized Schedule")
st.caption("Generate your optimized daily plan based on your owner preferences and priorities.")

if st.button("Generate Schedule"):
    if not all_tasks:
        st.warning("Please add at least one task before generating a schedule.")
    else:
        plan = scheduler.generate_daily_plan()
        
        st.info(f"💡 **Plan Explanation:**\n\n{plan['explanation']}")
        
        st.markdown("### 📋 Optimized Daily Plan Results:")
        
        for idx, task in enumerate(plan["schedule"], 1):
            pet_obj = scheduler.owner.pets.get(task.pet_id)
            pet_name = pet_obj.name if pet_obj else "Unknown"
            time_str = task.scheduled_time.strftime("%I:%M %p")
            
            with st.expander(f"{idx}. [{task.priority.upper()}] {task.description} — {pet_name} ({time_str})"):
                st.write(f"**Category:** {task.category}")
                st.write(f"**Duration:** {task.duration_minutes} minutes")
                st.write(f"**Frequency:** {task.frequency}")
                st.write(f"**Special Pet Notes:** {pet_obj.special_notes if pet_obj and pet_obj.special_notes else 'None'}")