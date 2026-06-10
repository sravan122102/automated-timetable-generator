from models import db, Assignment, TimeSlot, TimetableEntry, Classroom, TeacherAvailability

def generate_timetable(class_id=None):
    """
    Greedy scheduling algorithm for generating timetable.
    If class_id is None, generates for all classes.
    """
    # 1. Clear existing timetable entries for the targeted classes
    if class_id:
        entries_to_delete = TimetableEntry.query.join(Assignment).filter(Assignment.class_id == class_id).all()
        assignments = Assignment.query.filter_by(class_id=class_id).all()
    else:
        entries_to_delete = TimetableEntry.query.all()
        assignments = Assignment.query.all()
        
    for entry in entries_to_delete:
        db.session.delete(entry)
    db.session.commit()

    # 2. Fetch all time slots (excluding lunch breaks for scheduling)
    available_time_slots = TimeSlot.query.filter_by(is_lunch_break=False).order_by(TimeSlot.day_of_week, TimeSlot.period_number).all()
    
    # Pre-fetch existing entries for conflict checking
    existing_entries = TimetableEntry.query.all()
    
    class_schedule = {ts.id: [] for ts in existing_entries} # keep track of who is where

    for assignment in assignments:
        subject = assignment.subject
        teacher = assignment.teacher
        
        # Determine number of periods needed
        periods_needed = subject.weekly_hours
        needs_lab = subject.needs_lab
        
        # Get teacher availabilities
        t_avail = TeacherAvailability.query.filter_by(teacher_id=teacher.id).all()
        allowed_slots = [(a.day_of_week, a.period_number) for a in t_avail]

        # For scheduling, we'll try to find slots
        scheduled_periods = 0
        
        for slot in available_time_slots:
            if scheduled_periods >= periods_needed:
                break
                
            # Check teacher availability
            if allowed_slots and (slot.day_of_week, slot.period_number) not in allowed_slots:
                continue
                
            # Conflict Check 1: Is Teacher already busy at this slot?
            teacher_conflict = TimetableEntry.query.join(Assignment).filter(
                Assignment.teacher_id == teacher.id,
                TimetableEntry.time_slot_id == slot.id
            ).first()
            if teacher_conflict:
                continue
                
            # Conflict Check 2: Is Class already busy at this slot?
            class_conflict = TimetableEntry.query.join(Assignment).filter(
                Assignment.class_id == assignment.class_id,
                TimetableEntry.time_slot_id == slot.id
            ).first()
            if class_conflict:
                continue

            # Find an available classroom
            # If lab, needs a lab room. Otherwise regular.
            valid_classrooms = Classroom.query.filter_by(is_lab=needs_lab).all()
            room_to_assign = None
            
            for room in valid_classrooms:
                room_conflict = TimetableEntry.query.filter_by(
                    classroom_id=room.id,
                    time_slot_id=slot.id
                ).first()
                if not room_conflict:
                    room_to_assign = room
                    break
                    
            if not room_to_assign:
                continue
                
            # If lab, we need consecutive periods
            if needs_lab:
                # Find the next slot
                next_slot = TimeSlot.query.filter_by(
                    day_of_week=slot.day_of_week, 
                    period_number=slot.period_number + 1,
                    is_lunch_break=False
                ).first()
                
                if not next_slot:
                    continue # No next slot available on same day
                    
                # Check constraints for next slot
                teacher_conflict_next = TimetableEntry.query.join(Assignment).filter(
                    Assignment.teacher_id == teacher.id, TimetableEntry.time_slot_id == next_slot.id).first()
                class_conflict_next = TimetableEntry.query.join(Assignment).filter(
                    Assignment.class_id == assignment.class_id, TimetableEntry.time_slot_id == next_slot.id).first()
                room_conflict_next = TimetableEntry.query.filter_by(
                    classroom_id=room_to_assign.id, time_slot_id=next_slot.id).first()
                    
                if teacher_conflict_next or class_conflict_next or room_conflict_next:
                    continue
                    
                # Assign both slots
                entry1 = TimetableEntry(assignment_id=assignment.id, classroom_id=room_to_assign.id, time_slot_id=slot.id)
                entry2 = TimetableEntry(assignment_id=assignment.id, classroom_id=room_to_assign.id, time_slot_id=next_slot.id)
                db.session.add(entry1)
                db.session.add(entry2)
                db.session.commit()
                scheduled_periods += 2
            else:
                # Assign single slot
                entry = TimetableEntry(assignment_id=assignment.id, classroom_id=room_to_assign.id, time_slot_id=slot.id)
                db.session.add(entry)
                db.session.commit()
                scheduled_periods += 1

    return True
