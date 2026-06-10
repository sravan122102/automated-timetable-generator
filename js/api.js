const API_BASE = '/api';

class Api {
    static get token() {
        return localStorage.getItem('token');
    }

    static async request(endpoint, method = 'GET', body = null) {
        const headers = {
            'Content-Type': 'application/json'
        };
        
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        const config = {
            method,
            headers
        };

        if (body) {
            config.body = JSON.stringify(body);
        }

        try {
            const response = await fetch(`${API_BASE}${endpoint}`, config);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || 'Something went wrong');
            }
            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    // Auth
    static login(username, password) { return this.request('/login', 'POST', { username, password }); }
    
    // Stats
    static getStats() { return this.request('/stats'); }
    
    // Teachers
    static getTeachers() { return this.request('/teachers'); }
    static addTeacher(name) { return this.request('/teachers', 'POST', { name }); }
    static deleteTeacher(id) { return this.request(`/teachers/${id}`, 'DELETE'); }
    
    // Subjects
    static getSubjects() { return this.request('/subjects'); }
    static addSubject(data) { return this.request('/subjects', 'POST', data); }
    static deleteSubject(id) { return this.request(`/subjects/${id}`, 'DELETE'); }

    // Classrooms
    static getClassrooms() { return this.request('/classrooms'); }
    static addClassroom(data) { return this.request('/classrooms', 'POST', data); }
    static deleteClassroom(id) { return this.request(`/classrooms/${id}`, 'DELETE'); }
    
    // Classes
    static getClasses() { return this.request('/classes'); }
    static addClass(name) { return this.request('/classes', 'POST', { name }); }
    static deleteClass(id) { return this.request(`/classes/${id}`, 'DELETE'); }
    
    // Assignments
    static getAssignments() { return this.request('/assignments'); }
    static addAssignment(data) { return this.request('/assignments', 'POST', data); }
    
    // Generator
    static generate(class_id) { return this.request('/generate', 'POST', { class_id }); }
    
    // Timetable
    static getClassTimetable(id) { return this.request(`/timetable/class/${id}`); }
    static getTeacherTimetable(id) { return this.request(`/timetable/teacher/${id}`); }
}
