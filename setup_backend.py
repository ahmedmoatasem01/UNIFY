"""
Backend Setup Script for Unify AI Assistant
Initializes database tables and populates knowledge base
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from repositories.repository_factory import RepositoryFactory
from models.knowledge_base import KnowledgeBase

def setup_backend(force_populate=False):
    """Setup backend: create tables and populate knowledge base"""
    
    print("=" * 60)
    print("Unify AI Assistant - Backend Setup")
    print("=" * 60)
    print()
    
    # Step 1: Create tables
    print("[1/3] Creating database tables...")
    try:
        kb_repo = RepositoryFactory.get_repository('knowledge_base')
        kb_repo.create_table()
        print("  [+] Knowledge_Base table ready")
        
        chat_repo = RepositoryFactory.get_repository('chat_history')
        chat_repo.create_table()
        print("  [+] Chat_History table ready")
    except Exception as e:
        print(f"  [-] Error creating tables: {e}")
        return False
    
    # Step 2: Check existing data
    print()
    print("[2/3] Checking existing data...")
    try:
        existing_count = len(kb_repo.get_all())
        print(f"  [i] Found {existing_count} documents in knowledge base")
        
        if existing_count > 0 and not force_populate:
            print("  [i] Knowledge base already populated. Skipping...")
            print()
            print("To repopulate, run: python setup_backend.py --force")
            return True
    except Exception as e:
        print(f"  [-] Error checking data: {e}")
        existing_count = 0
    
    # Step 3: Populate knowledge base
    print()
    print("[3/3] Populating knowledge base...")
    
    knowledge_data = [
        # ==================== COURSES ====================
        {
            "title": "Data Structures - CS202",
            "content": "Data Structures (CS202) is a fundamental computer science course covering arrays, linked lists, stacks, queues, trees, graphs, and hash tables. Prerequisites: Programming Fundamentals (CS101). Credits: 4. Offered: Fall and Spring semesters.",
            "category": "Courses",
            "keywords": "data structures, algorithms, CS202, programming, computer science",
            "source": "Course Catalog 2024"
        },
        {
            "title": "Machine Learning - CS401",
            "content": "Machine Learning (CS401) covers supervised and unsupervised learning, neural networks, deep learning, and AI applications. Prerequisites: Data Structures (CS202), Linear Algebra (MATH201), Probability & Statistics (MATH301). Project-based course. Credits: 4. Lab included. Spring only.",
            "category": "Courses",
            "keywords": "machine learning, AI, neural networks, CS401, advanced course",
            "source": "Course Catalog 2024"
        },
        {
            "title": "Database Systems - CS305",
            "content": "Database Systems (CS305) covers relational database design, SQL, normalization, indexing, transaction processing, and NoSQL databases. Prerequisites: Data Structures (CS202). Credits: 3. Offered: Fall and Spring semesters. Lab included.",
            "category": "Courses",
            "keywords": "database, SQL, CS305, data management, relational",
            "source": "Course Catalog 2024"
        },
        {
            "title": "Operating Systems - CS310",
            "content": "Operating Systems (CS310) covers process management, memory management, file systems, I/O systems, and concurrency. Prerequisites: Computer Architecture (CS204), Data Structures (CS202). Credits: 3. Offered: Fall semester only.",
            "category": "Courses",
            "keywords": "operating systems, CS310, processes, memory, concurrency",
            "source": "Course Catalog 2024"
        },
        {
            "title": "Software Engineering - CS350",
            "content": "Software Engineering (CS350) covers software development lifecycle, design patterns, testing, project management, and team collaboration. Prerequisites: Data Structures (CS202), Object-Oriented Programming (CS203). Credits: 4. Includes semester-long team project.",
            "category": "Courses",
            "keywords": "software engineering, CS350, design patterns, project management",
            "source": "Course Catalog 2024"
        },
        {
            "title": "Linear Algebra - MATH201",
            "content": "Linear Algebra (MATH201) covers vectors, matrices, systems of linear equations, eigenvalues, eigenvectors, and linear transformations. Prerequisites: Calculus I (MATH101). Credits: 3. Offered: Fall and Spring semesters. Required for many CS courses.",
            "category": "Courses",
            "keywords": "linear algebra, MATH201, matrices, vectors, prerequisites",
            "source": "Course Catalog 2024"
        },
        {
            "title": "Probability and Statistics - MATH301",
            "content": "Probability and Statistics (MATH301) covers probability theory, random variables, distributions, hypothesis testing, and regression analysis. Prerequisites: Calculus II (MATH102). Credits: 3. Offered: Fall and Spring semesters.",
            "category": "Courses",
            "keywords": "probability, statistics, MATH301, distributions, data analysis",
            "source": "Course Catalog 2024"
        },
        
        # ==================== ACADEMIC POLICIES ====================
        {
            "title": "GPA Calculation Method",
            "content": "GPA is calculated on a 4.0 scale. A=4.0, A-=3.7, B+=3.3, B=3.0, B-=2.7, C+=2.3, C=2.0, C-=1.7, D+=1.3, D=1.0, F=0.0. Semester GPA = sum of (grade points x credits) / total credits. Cumulative GPA includes all semesters.",
            "category": "Academic Policies",
            "keywords": "GPA, grades, calculation, academic standing, grading scale",
            "source": "Student Handbook 2024"
        },
        {
            "title": "Academic Probation Policy",
            "content": "Students placed on academic probation if semester or cumulative GPA falls below 2.0. Probation conditions: meet advisor monthly, limit course load to 12 credits, mandatory tutoring. Dismissed if GPA remains below 2.0 after two consecutive semesters on probation.",
            "category": "Academic Policies",
            "keywords": "academic probation, dismissal, GPA requirements, policies",
            "source": "Student Handbook 2024"
        },
        {
            "title": "Graduation Requirements",
            "content": "Bachelor's degree requires 120-130 credits (varies by major). Minimum 2.0 cumulative GPA. Complete general education requirements, major requirements, and electives. Apply for graduation one semester before completion. Graduation fee: $150. Ceremony attendance optional.",
            "category": "Academic Policies",
            "keywords": "graduation, degree requirements, credits, commencement",
            "source": "Academic Requirements 2024"
        },
        {
            "title": "Grade Appeal Process",
            "content": "Students may appeal a final grade within 30 days of grade posting. Appeal process: 1) Discuss with instructor, 2) If unresolved, contact department chair, 3) File formal appeal with Registrar. Appeals must include documentation. Process typically takes 2-4 weeks.",
            "category": "Academic Policies",
            "keywords": "grade appeal, grades, dispute, registrar, academic policies",
            "source": "Student Handbook 2024"
        },
        {
            "title": "Withdrawal and Drop Policy",
            "content": "Students may drop courses without penalty during first two weeks. Withdrawal after week 2 results in 'W' grade (no GPA impact). Withdrawal after week 10 requires approval and results in 'WF' (counts as F). Medical withdrawals require documentation.",
            "category": "Academic Policies",
            "keywords": "withdrawal, drop, W grade, add drop period, deadlines",
            "source": "Academic Policies 2024"
        },
        {
            "title": "Credit Hour Policy",
            "content": "One credit hour = 1 hour of classroom instruction + 2 hours of outside work per week. Full-time status: 12+ credits. Maximum load without approval: 18 credits. Overload requires 3.0+ GPA and advisor approval. Summer maximum: 9 credits.",
            "category": "Academic Policies",
            "keywords": "credits, credit hours, full-time, course load, enrollment",
            "source": "Academic Policies 2024"
        },
        {
            "title": "Incomplete Grade Policy",
            "content": "Incomplete (I) grades may be assigned when student completes 75%+ of work but cannot finish due to extenuating circumstances. Student and instructor must agree on completion deadline (max 1 year). If not completed, 'I' converts to 'F'.",
            "category": "Academic Policies",
            "keywords": "incomplete, I grade, extensions, deadlines, academic policies",
            "source": "Academic Policies 2024"
        },
        
        # ==================== REGISTRATION ====================
        {
            "title": "Course Registration Deadlines",
            "content": "Course registration for Fall semester opens July 1st and closes August 15th. Spring semester registration runs November 1st to December 15th. Late registration (with fee) available first week of semester. Add/drop deadline: end of second week.",
            "category": "Registration",
            "keywords": "registration, deadlines, add drop, enrollment, dates",
            "source": "Academic Calendar 2024"
        },
        {
            "title": "Transfer Credit Policy",
            "content": "Transfer credits accepted from accredited institutions. Official transcripts required. C grade or better transfers. Maximum 60 credits from 2-year college, 90 from 4-year. Evaluation takes 2-4 weeks. Contact Registrar with questions. AP/IB credits also accepted per policy.",
            "category": "Registration",
            "keywords": "transfer credits, transcripts, AP credits, credit evaluation",
            "source": "Registrar Office 2024"
        },
        {
            "title": "Prerequisites and Co-requisites",
            "content": "Prerequisites must be completed before enrolling. Co-requisites must be taken simultaneously. Prerequisite waivers require department approval. System automatically checks prerequisites during registration. Missing prerequisites may result in automatic drop.",
            "category": "Registration",
            "keywords": "prerequisites, co-requisites, requirements, enrollment, registration",
            "source": "Registration Guide 2024"
        },
        {
            "title": "Waitlist Process",
            "content": "Students may join waitlist if course is full. Waitlist operates automatically: when spot opens, next student is enrolled (if prerequisites met). Waitlist closes first day of classes. Check email regularly if on waitlist. Maximum 3 waitlist positions allowed.",
            "category": "Registration",
            "keywords": "waitlist, full classes, enrollment, registration",
            "source": "Registration Guide 2024"
        },
        
        # ==================== EXAMS ====================
        {
            "title": "Exam Policies and Procedures",
            "content": "Final exams scheduled during finals week. No early or makeup exams except medical emergency (doctor's note required). Students must bring ID. Closed-book unless specified. Academic integrity policy strictly enforced. Violations result in failing grade or expulsion.",
            "category": "Exams",
            "keywords": "exams, finals, policies, academic integrity, procedures",
            "source": "Exam Guidelines 2024"
        },
        {
            "title": "Final Exam Schedule",
            "content": "Final exams scheduled during last week of semester. Schedule posted mid-semester. Conflicts: contact Registrar within 2 weeks of schedule posting. Students with 3+ exams in 24 hours may request reschedule. Exam times based on first class meeting time.",
            "category": "Exams",
            "keywords": "final exams, exam schedule, conflicts, finals week",
            "source": "Academic Calendar 2024"
        },
        {
            "title": "Midterm Exam Policies",
            "content": "Midterm exams typically held weeks 7-8. Faculty may schedule midterms outside normal class time with advance notice. Students must be notified at least 2 weeks prior. Maximum 2 midterms per course. Makeup exams require valid excuse and documentation.",
            "category": "Exams",
            "keywords": "midterms, exams, testing, academic policies",
            "source": "Exam Guidelines 2024"
        },
        
        # ==================== FEES & FINANCIAL ====================
        {
            "title": "Financial Aid Options",
            "content": "Financial aid includes scholarships, grants, student loans, and work-study programs. FAFSA required. Merit scholarships: 3.5+ GPA. Need-based aid available. Application deadline: March 1st for priority consideration. Contact Financial Aid Office for details.",
            "category": "Fees",
            "keywords": "financial aid, scholarships, grants, loans, FAFSA, tuition",
            "source": "Financial Aid Guide 2024"
        },
        {
            "title": "Tuition and Fees Structure",
            "content": "Undergraduate tuition: $X per credit hour (full-time: flat rate for 12-18 credits). Fees: Technology ($200/semester), Student Activity ($150/semester), Health ($300/semester). Payment plans available. Late payment fee: $50. Payment due 2 weeks before semester start.",
            "category": "Fees",
            "keywords": "tuition, fees, payment, costs, financial",
            "source": "Bursar Office 2024"
        },
        {
            "title": "Scholarship Opportunities",
            "content": "Merit scholarships: 3.5+ GPA, renewable with 3.0+ GPA. Department scholarships available by major. External scholarships listed on website. Application deadlines vary. Athletic scholarships handled by Athletics Department. Need-based scholarships require FAFSA.",
            "category": "Fees",
            "keywords": "scholarships, financial aid, merit, awards, funding",
            "source": "Financial Aid Office 2024"
        },
        
        # ==================== CAMPUS SERVICES ====================
        {
            "title": "Library Hours and Services",
            "content": "Main Library hours: Monday-Thursday 7am-midnight, Friday 7am-8pm, Saturday 9am-6pm, Sunday 10am-midnight. Services include study rooms, computer labs, research assistance, and inter-library loans. 24/7 online resources access.",
            "category": "Campus",
            "keywords": "library, hours, services, study rooms, resources",
            "source": "Library Services 2024"
        },
        {
            "title": "Campus Security and Safety",
            "content": "Campus Security operates 24/7. Emergency number: ext. 911. Services include campus patrols, escort service (6pm-2am), emergency phones throughout campus, security cameras, and safety education programs. Download SafeCampus app for alerts and assistance.",
            "category": "Campus",
            "keywords": "security, safety, emergency, campus police, protection",
            "source": "Security Office 2024"
        },
        {
            "title": "Housing and Residence Halls",
            "content": "On-campus housing guaranteed for freshmen. Options: traditional dorms, suites, apartments. Housing application opens March 1st. Roommate matching available. All rooms have WiFi, furniture, utilities included. RA support 24/7. Meal plans required for dorm residents.",
            "category": "Campus",
            "keywords": "housing, dorms, residence halls, roommates, campus life",
            "source": "Housing Services 2024"
        },
        {
            "title": "Dining Services",
            "content": "Three dining halls on campus plus food court, cafes, and convenience stores. Meal plans: Unlimited ($X), 14 meals/week ($X), 10 meals/week ($X), or block plans. Dietary accommodations available. Hours: Dining halls 7am-9pm, cafes vary. Mobile ordering available.",
            "category": "Campus",
            "keywords": "dining, food, meal plans, cafeteria, restaurants",
            "source": "Dining Services 2024"
        },
        {
            "title": "Parking and Transportation",
            "content": "Parking permits required: Student ($150/year), Commuter ($100/semester). Shuttle service runs 7am-10pm between campus and nearby areas. Bike share program available. Public transit discounts with student ID. Carpooling encouraged. Parking violations: $25-100 fines.",
            "category": "Campus",
            "keywords": "parking, transportation, shuttle, permits, commuting",
            "source": "Transportation Services 2024"
        },
        {
            "title": "IT Services and Computer Labs",
            "content": "IT Help Desk: Monday-Friday 8am-8pm, Weekends 10am-4pm. Computer labs in Library, Engineering Building, and Student Center. Free software: Microsoft Office, MATLAB, Adobe Creative Suite. WiFi campus-wide. Student email: username@university.edu. Password resets via portal.",
            "category": "Campus",
            "keywords": "IT, technology, computer labs, WiFi, email, help desk",
            "source": "IT Services 2024"
        },
        
        # ==================== RESOURCES ====================
        {
            "title": "Career Services and Internships",
            "content": "Career Services offers resume review, interview prep, job fairs, and internship placement. Free for all students and alumni. Walk-in hours Monday-Friday 9am-5pm. Online job board with 500+ postings. Internship credit available for approved positions.",
            "category": "Resources",
            "keywords": "career services, internships, jobs, resume, interview",
            "source": "Career Center 2024"
        },
        {
            "title": "Student Health Services",
            "content": "Health Center provides medical care, counseling, wellness programs. Open Monday-Friday 8am-5pm. After-hours nurse line available. Insurance accepted. Services include primary care, mental health counseling, immunizations, and health education. All visits confidential.",
            "category": "Resources",
            "keywords": "health services, medical, counseling, wellness, mental health",
            "source": "Health Center 2024"
        },
        {
            "title": "Study Abroad Programs",
            "content": "Study abroad opportunities available in 20+ countries. Semester or year-long programs. Application deadline: October 15th (spring), March 15th (fall/year). Minimum 3.0 GPA required. Financial aid applies. Contact International Programs Office.",
            "category": "Resources",
            "keywords": "study abroad, international, exchange programs, travel",
            "source": "International Programs 2024"
        },
        {
            "title": "Tutoring and Academic Support",
            "content": "Free tutoring available in Math, Science, Writing, and major courses. Tutoring Center hours: Monday-Thursday 9am-9pm, Friday 9am-5pm. Group and individual sessions. Peer tutors and professional staff. Drop-in or appointment. Online tutoring available. Subject-specific labs: Math Lab, Writing Center, Science Center.",
            "category": "Resources",
            "keywords": "tutoring, academic support, help, study help, learning center",
            "source": "Academic Support Center 2024"
        },
        {
            "title": "Disability Services",
            "content": "Disability Services provides accommodations for students with documented disabilities. Services: extended test time, note-taking, accessible housing, assistive technology, sign language interpreters. Registration required with documentation. Contact before semester starts for best service.",
            "category": "Resources",
            "keywords": "disability, accommodations, accessibility, support services",
            "source": "Disability Services 2024"
        },
        {
            "title": "Student Organizations and Clubs",
            "content": "200+ student organizations: academic, cultural, recreational, service, Greek life. Club fair at start of each semester. To start new club: minimum 10 members, faculty advisor, constitution. Funding available through Student Government. Activities calendar on website.",
            "category": "Resources",
            "keywords": "clubs, organizations, student groups, activities, involvement",
            "source": "Student Activities 2024"
        },
        {
            "title": "Recreation and Fitness",
            "content": "Student Recreation Center: Cardio equipment, weight room, basketball courts, pool, rock climbing wall. Hours: 6am-midnight weekdays, 8am-10pm weekends. Group fitness classes included. Intramural sports: basketball, soccer, volleyball, flag football. Equipment rental available.",
            "category": "Resources",
            "keywords": "gym, fitness, recreation, sports, workout, exercise",
            "source": "Recreation Center 2024"
        },
        
        # ==================== NEW CATEGORIES ====================
        {
            "title": "Academic Advising",
            "content": "All students assigned academic advisor by major. Required meetings: once per semester for registration approval. Walk-in hours available. Advisors help with course selection, degree planning, career guidance, and academic issues. Change advisor through department office.",
            "category": "Academic Support",
            "keywords": "advising, advisor, academic planning, course selection, guidance",
            "source": "Academic Advising Office 2024"
        },
        {
            "title": "Research Opportunities",
            "content": "Undergraduate research opportunities available in all departments. Research credits: 1-3 credits per semester. Apply with faculty members conducting research. Summer research programs available. Research symposium held annually. Publication and presentation opportunities.",
            "category": "Academic Support",
            "keywords": "research, undergraduate research, faculty, opportunities",
            "source": "Research Office 2024"
        },
        {
            "title": "Honors Program",
            "content": "Honors Program: GPA 3.5+, special courses, priority registration, thesis project. Benefits: smaller classes, research opportunities, honors housing option, graduation distinction. Application deadline: March 1st for incoming students. Current students: apply by end of sophomore year.",
            "category": "Academic Support",
            "keywords": "honors, honors program, distinction, advanced courses",
            "source": "Honors Program 2024"
        },
        {
            "title": "Course Evaluation Process",
            "content": "Students evaluate courses anonymously at end of each semester. Evaluations available online last 2 weeks of semester. Results used for faculty development and course improvement. Evaluations required before viewing final grades. Response rate affects department funding.",
            "category": "Academic Policies",
            "keywords": "course evaluation, feedback, surveys, ratings",
            "source": "Academic Affairs 2024"
        },
        {
            "title": "Academic Calendar Overview",
            "content": "Fall semester: Late August to mid-December (16 weeks). Spring semester: Mid-January to early May (16 weeks). Summer sessions: May-June (4 weeks), June-July (4 weeks), May-July (8 weeks). Breaks: Fall break (3 days), Thanksgiving (4 days), Spring break (1 week).",
            "category": "Academic Policies",
            "keywords": "calendar, semester dates, breaks, academic year",
            "source": "Academic Calendar 2024"
        },
        {
            "title": "Textbook and Course Materials",
            "content": "Textbooks available at University Bookstore and online. Bookstore price match guarantee. Rentals available for many texts. Some courses use digital materials included in course fee. Check course syllabus before purchasing. Sell-back at end of semester for cash or store credit.",
            "category": "Academic Support",
            "keywords": "textbooks, course materials, bookstore, rentals",
            "source": "Bookstore 2024"
        },
        {
            "title": "Student Email and Communication",
            "content": "All students receive university email account (username@university.edu). Official communications sent to university email only. Check daily. Forward to personal email allowed. Email storage: 50GB. Microsoft 365 included (Word, Excel, PowerPoint, Teams, OneDrive). Access via web or mobile app.",
            "category": "Technology",
            "keywords": "email, Microsoft 365, communication, Office, OneDrive",
            "source": "IT Services 2024"
        },
        {
            "title": "Learning Management System (LMS)",
            "content": "Course materials, assignments, grades, and announcements on LMS platform. Login with university credentials. Mobile app available. Submit assignments, take quizzes, participate in discussions. Grades posted within 2 weeks of assignment due date. Contact IT if access issues.",
            "category": "Technology",
            "keywords": "LMS, online learning, assignments, grades, course materials",
            "source": "IT Services 2024"
        },
        {
            "title": "Student ID Card Services",
            "content": "Student ID required for library, dining, events, building access. Get ID at Card Services Office (Student Center, Room 100). Hours: Monday-Friday 8am-5pm. Replacement fee: $20. ID used for printing, vending machines, and campus discounts. Photo ID required for pickup.",
            "category": "Campus",
            "keywords": "student ID, ID card, identification, access card",
            "source": "Card Services 2024"
        },
        {
            "title": "Printing and Copy Services",
            "content": "Printing available in Library, computer labs, Student Center. Students receive $10 printing credit per semester. Additional pages: $0.10/page black & white, $0.50/page color. Add funds via online portal. Copy services in Library and Student Center. Large format printing available.",
            "category": "Technology",
            "keywords": "printing, copies, printing credit, documents",
            "source": "IT Services 2024"
        }
    ]
    
    success_count = 0
    for data in knowledge_data:
        try:
            kb = KnowledgeBase(
                title=data["title"],
                content=data["content"],
                category=data["category"],
                keywords=data["keywords"],
                source=data["source"]
            )
            kb_repo.add(kb)
            success_count += 1
            print(f"  [+] Added: {data['title']}")
        except Exception as e:
            print(f"  [-] Failed: {data['title']} - {str(e)[:50]}")
    
    print()
    print(f"[SUCCESS] Populated {success_count}/{len(knowledge_data)} documents")
    print()
    
    # Step 4: Verify
    print("Verification:")
    final_count = len(kb_repo.get_all())
    categories = kb_repo.get_categories()
    print(f"  [i] Total documents: {final_count}")
    print(f"  [i] Categories: {len(categories)}")
    for cat in categories:
        cat_docs = kb_repo.search_by_category(cat)
        print(f"      - {cat}: {len(cat_docs)} documents")
    
    print()
    print("=" * 60)
    print("Backend setup complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("  1. Start the app: python app.py")
    print("  2. Open AI Assistant: http://localhost:5000/ai-assistant/")
    print("  3. Ask questions and test the AI!")
    print()
    
    return True

if __name__ == "__main__":
    force = "--force" in sys.argv or "-f" in sys.argv
    try:
        success = setup_backend(force_populate=force)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n[!] Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERROR] Setup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

