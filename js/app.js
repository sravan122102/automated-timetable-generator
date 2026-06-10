// --- GLOBAL STATE & ROUTING ---
let currentView = '';

document.addEventListener('DOMContentLoaded', () => {
    checkAuth();

    document.getElementById('login-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const user = document.getElementById('username').value;
        const pass = document.getElementById('password').value;
        const errorDiv = document.getElementById('login-error');
        try {
            const data = await Api.login(user, pass);
            localStorage.setItem('token', data.token);
            checkAuth();
        } catch (err) {
            errorDiv.textContent = err.message;
        }
    });

    document.getElementById('logout-btn').addEventListener('click', () => {
        localStorage.removeItem('token');
        checkAuth();
    });

    window.addEventListener('hashchange', handleRoute);
});

function checkAuth() {
    if (Api.token) {
        document.getElementById('login-view').classList.add('hidden');
        document.getElementById('app-container').classList.remove('hidden');
        if (!window.location.hash) {
            window.location.hash = '#dashboard';
        } else {
            handleRoute();
        }
    } else {
        document.getElementById('login-view').classList.remove('hidden');
        document.getElementById('app-container').classList.add('hidden');
    }
}

async function handleRoute() {
    const hash = window.location.hash.replace('#', '') || 'dashboard';
    currentView = hash;
    
    // Update active nav
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('data-view') === hash) {
            link.classList.add('active');
        }
    });

    // Fetch view
    try {
        const response = await fetch(`views/${hash}.html`);
        const html = await response.text();
        document.getElementById('view-container').innerHTML = html;
        
        // Initialize view data
        initView(hash);
    } catch (err) {
        console.error('Error loading view:', err);
    }
}

async function initView(view) {
    try {
        if (view === 'dashboard') {
            const stats = await Api.getStats();
            document.getElementById('stat-teachers').textContent = stats.teachers;
            document.getElementById('stat-subjects').textContent = stats.subjects;
            document.getElementById('stat-classrooms').textContent = stats.classrooms;
            document.getElementById('stat-classes').textContent = stats.classes;
        } 
        else if (view === 'teachers') {
            loadTeachers();
        }
        else if (view === 'subjects') {
            loadSubjects();
        }
        else if (view === 'classrooms') {
            loadClassrooms();
        }
        else if (view === 'classes') {
            loadClasses();
        }
        else if (view === 'assignments') {
            loadAssignments();
            populateAssignmentDropdowns();
        }
        else if (view === 'generator') {
            populateGeneratorDropdown();
        }
        else if (view === 'timetable') {
            populateTimetableDropdowns();
            renderEmptyGrid();
        }
    } catch (e) {
        console.error('Error initializing view:', e);
        if (e.message.includes('401')) {
            localStorage.removeItem('token');
            checkAuth();
        }
    }
}

// --- MODALS ---
window.openModal = (id) => {
    document.getElementById(id).classList.add('active');
}

window.closeModal = (id) => {
    document.getElementById(id).classList.remove('active');
}

// --- TEACHERS ---
async function loadTeachers() {
    const teachers = await Api.getTeachers();
    const tbody = document.getElementById('teachers-table-body');
    tbody.innerHTML = teachers.map(t => `
        <tr>
            <td>${t.id}</td>
            <td>${t.name}</td>
            <td>
                <button class="btn-icon" style="color:var(--danger)" onclick="deleteTeacher(${t.id})"><i class="fa-solid fa-trash"></i></button>
            </td>
        </tr>
    `).join('');
}

window.handleAddTeacher = async (e) => {
    e.preventDefault();
    const name = document.getElementById('teacher-name').value;
    await Api.addTeacher(name);
    closeModal('addTeacherModal');
    loadTeachers();
}

window.deleteTeacher = async (id) => {
    if(confirm('Delete teacher?')) {
        await Api.deleteTeacher(id);
        loadTeachers();
    }
}

// --- SUBJECTS ---
async function loadSubjects() {
    const subjects = await Api.getSubjects();
    const tbody = document.getElementById('subjects-table-body');
    tbody.innerHTML = subjects.map(s => `
        <tr>
            <td>${s.id}</td>
            <td>${s.name}</td>
            <td>${s.weekly_hours}</td>
            <td>${s.needs_lab ? 'Yes' : 'No'}</td>
            <td>
                <button class="btn-icon" style="color:var(--danger)" onclick="deleteSubject(${s.id})"><i class="fa-solid fa-trash"></i></button>
            </td>
        </tr>
    `).join('');
}

window.handleAddSubject = async (e) => {
    e.preventDefault();
    const data = {
        name: document.getElementById('subject-name').value,
        weekly_hours: parseInt(document.getElementById('subject-hours').value),
        needs_lab: document.getElementById('subject-lab').checked
    };
    await Api.addSubject(data);
    closeModal('addSubjectModal');
    loadSubjects();
}

window.deleteSubject = async (id) => {
    if(confirm('Delete subject?')) {
        await Api.deleteSubject(id);
        loadSubjects();
    }
}

// --- CLASSROOMS ---
async function loadClassrooms() {
    const rooms = await Api.getClassrooms();
    const tbody = document.getElementById('classrooms-table-body');
    tbody.innerHTML = rooms.map(r => `
        <tr>
            <td>${r.id}</td>
            <td>${r.name}</td>
            <td>${r.capacity}</td>
            <td>${r.is_lab ? 'Yes' : 'No'}</td>
            <td>
                <button class="btn-icon" style="color:var(--danger)" onclick="deleteClassroom(${r.id})"><i class="fa-solid fa-trash"></i></button>
            </td>
        </tr>
    `).join('');
}

window.handleAddClassroom = async (e) => {
    e.preventDefault();
    const data = {
        name: document.getElementById('room-name').value,
        capacity: parseInt(document.getElementById('room-capacity').value),
        is_lab: document.getElementById('room-lab').checked
    };
    await Api.addClassroom(data);
    closeModal('addClassroomModal');
    loadClassrooms();
}

window.deleteClassroom = async (id) => {
    if(confirm('Delete classroom?')) {
        await Api.deleteClassroom(id);
        loadClassrooms();
    }
}

// --- CLASSES ---
async function loadClasses() {
    const classes = await Api.getClasses();
    const tbody = document.getElementById('classes-table-body');
    tbody.innerHTML = classes.map(c => `
        <tr>
            <td>${c.id}</td>
            <td>${c.name}</td>
            <td>
                <button class="btn-icon" style="color:var(--danger)" onclick="deleteClass(${c.id})"><i class="fa-solid fa-trash"></i></button>
            </td>
        </tr>
    `).join('');
}

window.handleAddClass = async (e) => {
    e.preventDefault();
    const name = document.getElementById('class-name').value;
    await Api.addClass(name);
    closeModal('addClassModal');
    loadClasses();
}

window.deleteClass = async (id) => {
    if(confirm('Delete class?')) {
        await Api.deleteClass(id);
        loadClasses();
    }
}

// --- ASSIGNMENTS ---
async function loadAssignments() {
    const assigns = await Api.getAssignments();
    const tbody = document.getElementById('assignments-table-body');
    tbody.innerHTML = assigns.map(a => `
        <tr>
            <td>${a.id}</td>
            <td>${a.class_name}</td>
            <td>${a.subject_name}</td>
            <td>${a.teacher_name}</td>
        </tr>
    `).join('');
}

async function populateAssignmentDropdowns() {
    const [classes, subjects, teachers] = await Promise.all([
        Api.getClasses(), Api.getSubjects(), Api.getTeachers()
    ]);
    
    document.getElementById('assign-class').innerHTML = classes.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
    document.getElementById('assign-subject').innerHTML = subjects.map(s => `<option value="${s.id}">${s.name}</option>`).join('');
    document.getElementById('assign-teacher').innerHTML = teachers.map(t => `<option value="${t.id}">${t.name}</option>`).join('');
}

window.handleAddAssignment = async (e) => {
    e.preventDefault();
    const data = {
        class_id: parseInt(document.getElementById('assign-class').value),
        subject_id: parseInt(document.getElementById('assign-subject').value),
        teacher_id: parseInt(document.getElementById('assign-teacher').value)
    };
    await Api.addAssignment(data);
    closeModal('addAssignmentModal');
    loadAssignments();
}

// --- GENERATOR ---
async function populateGeneratorDropdown() {
    const classes = await Api.getClasses();
    const select = document.getElementById('generate-class');
    select.innerHTML = '<option value="">-- All Classes --</option>' + 
        classes.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
}

window.handleGenerate = async () => {
    const btn = document.getElementById('btn-generate');
    const resDiv = document.getElementById('generate-result');
    const classId = document.getElementById('generate-class').value;
    
    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Generating...';
    resDiv.textContent = '';
    resDiv.style.color = '';
    
    try {
        const res = await Api.generate(classId ? parseInt(classId) : null);
        resDiv.textContent = res.message;
        resDiv.style.color = 'var(--secondary)';
    } catch(err) {
        resDiv.textContent = err.message;
        resDiv.style.color = 'var(--danger)';
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="fa-solid fa-wand-magic-sparkles"></i> Generate Timetable';
    }
}

// --- TIMETABLE VIEW ---
const DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
const PERIODS = 8;
const LUNCH_PERIOD = 5;

async function populateTimetableDropdowns() {
    const [classes, teachers] = await Promise.all([
        Api.getClasses(), Api.getTeachers()
    ]);
    
    document.getElementById('view-class-select').innerHTML = '<option value="">-- Select --</option>' + 
        classes.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
        
    document.getElementById('view-teacher-select').innerHTML = '<option value="">-- Select --</option>' + 
        teachers.map(t => `<option value="${t.id}">${t.name}</option>`).join('');
}

function renderEmptyGrid() {
    const grid = document.getElementById('timetable-grid');
    let html = `<div class="timetable-cell header">Day/Period</div>`;
    
    for(let i=1; i<=PERIODS; i++) {
        html += `<div class="timetable-cell header">P${i}</div>`;
    }
    
    for(let d=0; d<DAYS.length; d++) {
        html += `<div class="timetable-cell day">${DAYS[d]}</div>`;
        for(let p=1; p<=PERIODS; p++) {
            if(p === LUNCH_PERIOD && d === 0) {
                html += `<div class="timetable-cell lunch-break">LUNCH</div>`;
            } else if (p === LUNCH_PERIOD) {
                // Skip rendering cell, grid-row span handles it
            } else {
                html += `<div class="timetable-cell" id="cell-${DAYS[d]}-${p}"></div>`;
            }
        }
    }
    grid.innerHTML = html;
}

window.loadClassTimetable = async () => {
    document.getElementById('view-teacher-select').value = '';
    const classId = document.getElementById('view-class-select').value;
    if(!classId) return;
    
    const className = document.getElementById('view-class-select').options[document.getElementById('view-class-select').selectedIndex].text;
    document.getElementById('timetable-title').textContent = `Timetable for ${className}`;
    
    renderEmptyGrid();
    try {
        const entries = await Api.getClassTimetable(classId);
        entries.forEach(e => {
            const cell = document.getElementById(`cell-${e.day}-${e.period}`);
            if(cell) {
                cell.innerHTML = `
                    <div class="subject">${e.subject}</div>
                    <div class="teacher">${e.teacher}</div>
                    <div class="room">${e.classroom}</div>
                `;
            }
        });
    } catch(err) {
        console.error(err);
    }
}

window.loadTeacherTimetable = async () => {
    document.getElementById('view-class-select').value = '';
    const teacherId = document.getElementById('view-teacher-select').value;
    if(!teacherId) return;
    
    const teacherName = document.getElementById('view-teacher-select').options[document.getElementById('view-teacher-select').selectedIndex].text;
    document.getElementById('timetable-title').textContent = `Timetable for ${teacherName}`;
    
    renderEmptyGrid();
    try {
        const entries = await Api.getTeacherTimetable(teacherId);
        entries.forEach(e => {
            const cell = document.getElementById(`cell-${e.day}-${e.period}`);
            if(cell) {
                cell.innerHTML = `
                    <div class="subject">${e.subject}</div>
                    <div class="teacher">${e.class_name}</div>
                    <div class="room">${e.classroom}</div>
                `;
            }
        });
    } catch(err) {
        console.error(err);
    }
}

// --- PDF EXPORT ---
window.exportToPDF = () => {
    const element = document.getElementById('timetable-export-area');
    const title = document.getElementById('timetable-title').textContent;
    
    const opt = {
      margin:       0.5,
      filename:     `${title.replace(/ /g, '_')}.pdf`,
      image:        { type: 'jpeg', quality: 0.98 },
      html2canvas:  { scale: 2 },
      jsPDF:        { unit: 'in', format: 'letter', orientation: 'landscape' }
    };

    html2pdf().set(opt).from(element).save();
}
