"""
Script to populate the knowledge base with sample data
Run this to initialize the AI Assistant with sample information
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from repositories.repository_factory import RepositoryFactory
from models.knowledge_base import KnowledgeBase

# Sample knowledge base data
SAMPLE_DATA = [
    # Course Information
    {
        'title': 'Computer Science Program Requirements',
        'content': '''The Computer Science program at Zewail City requires 120 credit hours for graduation. Students must complete:
- 45 credits of Core Computer Science courses
- 30 credits of Mathematics and Science courses
- 15 credits of General Education courses
- 30 credits of Electives and Free Choice courses

Core courses include: Introduction to Programming, Data Structures, Algorithms, Computer Architecture, Operating Systems, Database Systems, Software Engineering, and Computer Networks.''',
        'category': 'Academic Programs',
        'keywords': 'computer science, requirements, graduation, credits, courses, core courses, program',
        'source': 'Academic Catalog 2024'
    },
    {
        'title': 'Data Structures Course (CS202)',
        'content': '''Data Structures (CS202) is a fundamental course covering essential data structures and their applications. 

Prerequisites: Introduction to Programming (CS101)

Topics covered:
- Arrays and Linked Lists
- Stacks and Queues
- Trees (Binary, BST, AVL)
- Graphs and Graph Algorithms
- Hash Tables
- Sorting and Searching Algorithms

Credit Hours: 3
Offered: Fall and Spring semesters''',
        'category': 'Courses',
        'keywords': 'data structures, CS202, prerequisites, CS101, programming, algorithms',
        'source': 'Course Catalog'
    },
    {
        'title': 'Machine Learning Course (CS401)',
        'content': '''Machine Learning (CS401) introduces fundamental concepts and algorithms in machine learning.

Prerequisites: Data Structures (CS202), Linear Algebra (MATH201), Probability and Statistics (MATH301)

Topics covered:
- Supervised Learning (Regression, Classification)
- Unsupervised Learning (Clustering, Dimensionality Reduction)
- Neural Networks and Deep Learning
- Model Evaluation and Selection
- Real-world Applications

Credit Hours: 3
Offered: Spring semester only
Lab component included''',
        'category': 'Courses',
        'keywords': 'machine learning, CS401, AI, neural networks, deep learning, prerequisites',
        'source': 'Course Catalog'
    },
    
    # Academic Policies
    {
        'title': 'Course Registration Deadlines',
        'content': '''Course registration follows a strict timeline each semester:

Fall Semester:
- Registration Period: August 15-30
- Add/Drop Period: First two weeks of semester
- Late Registration Fee: Applies after August 30

Spring Semester:
- Registration Period: January 10-25
- Add/Drop Period: First two weeks of semester
- Late Registration Fee: Applies after January 25

Students must register during the designated period to avoid late fees. The add/drop period allows students to adjust their schedule without penalty.''',
        'category': 'Academic Policies',
        'keywords': 'registration, deadlines, add drop, semester, fall, spring, dates',
        'source': 'Academic Calendar 2024'
    },
    {
        'title': 'GPA Calculation Method',
        'content': '''Grade Point Average (GPA) is calculated using the following formula:

GPA = (Sum of Grade Points × Credit Hours) / Total Credit Hours

Grade Point Scale:
- A: 4.0
- A-: 3.7
- B+: 3.3
- B: 3.0
- B-: 2.7
- C+: 2.3
- C: 2.0
- C-: 1.7
- D: 1.0
- F: 0.0

Example: If you earn an A (4.0) in a 3-credit course and a B (3.0) in a 4-credit course:
GPA = (4.0×3 + 3.0×4) / (3+4) = 24/7 = 3.43

Minimum GPA for good academic standing: 2.0
Minimum GPA for graduation: 2.5''',
        'category': 'Academic Policies',
        'keywords': 'GPA, grade point average, calculation, grades, academic standing',
        'source': 'Student Handbook'
    },
    {
        'title': 'Academic Probation Policy',
        'content': '''Students whose cumulative GPA falls below 2.0 are placed on academic probation.

Probation Terms:
- Student must meet with academic advisor each semester
- Course load may be reduced (maximum 12 credits)
- Must achieve semester GPA of 2.5 or higher
- Probation lasts until cumulative GPA reaches 2.0

Consequences of Continued Probation:
- Two consecutive semesters: Required academic success workshops
- Three consecutive semesters: Academic suspension for one semester
- After suspension: Readmission requires petition and plan

Students on probation are not eligible for:
- Leadership positions in student organizations
- Participation in study abroad programs
- Certain scholarships and financial aid''',
        'category': 'Academic Policies',
        'keywords': 'probation, academic probation, GPA, suspension, requirements, consequences',
        'source': 'Student Handbook'
    },
    
    # Campus Resources
    {
        'title': 'Library Services and Hours',
        'content': '''The Zewail City Library provides comprehensive resources and services:

Operating Hours:
- Sunday-Thursday: 8:00 AM - 10:00 PM
- Friday: 9:00 AM - 5:00 PM
- Saturday: Closed
- During Exams: Extended hours (24/7 during finals week)

Services Available:
- Book borrowing (14-day loan period)
- Digital database access (IEEE, ACM, Science Direct)
- Study rooms (bookable via library website)
- Research assistance
- Printing and scanning services
- Group study areas
- Silent study zones

Students can access digital resources remotely using their student ID and password.''',
        'category': 'Campus Resources',
        'keywords': 'library, hours, services, books, study rooms, resources, databases',
        'source': 'Library Services Website'
    },
    {
        'title': 'Student Health Services',
        'content': '''The Student Health Center provides medical services to all enrolled students:

Location: Building A, Ground Floor
Hours: Sunday-Thursday, 9:00 AM - 4:00 PM

Services Provided:
- General medical consultations
- Emergency first aid
- Prescription medications
- Mental health counseling
- Vaccination programs
- Health education workshops

Emergency Contact: ext. 2500 (available 24/7)

Students must present their ID card for all services. Most services are free, but some medications may require copayment.''',
        'category': 'Campus Resources',
        'keywords': 'health, medical, clinic, health center, emergency, counseling, services',
        'source': 'Health Services Department'
    },
    {
        'title': 'Career Services and Internships',
        'content': '''The Career Development Center helps students with career planning and job placement:

Services Offered:
- Resume and CV review
- Interview preparation workshops
- Career counseling sessions
- Job fair organization
- Internship placement assistance
- Networking events with industry professionals

Internship Requirements:
- Available to students who have completed 60 credit hours
- Duration: 8-12 weeks (summer or semester)
- Can be credited (3 credits) if approved
- Must submit internship report and supervisor evaluation

Contact: careers@zewailcity.edu.eg
Office: Building C, 3rd Floor
Walk-in Hours: Sunday & Tuesday, 2:00-4:00 PM''',
        'category': 'Campus Resources',
        'keywords': 'career, internship, job, resume, career services, employment, placement',
        'source': 'Career Development Center'
    },
    
    # Student Life
    {
        'title': 'Student Housing Information',
        'content': '''Zewail City provides on-campus housing for students:

Housing Options:
- Single rooms (limited availability)
- Double occupancy rooms (standard)
- Apartment-style suites (for senior students)

Facilities:
- Wi-Fi connectivity
- Study lounges
- Laundry facilities
- Common kitchens
- 24/7 security

Housing Costs:
- Double room: 12,000 EGP per semester
- Single room: 18,000 EGP per semester
- Apartments: 22,000 EGP per semester

Application Process:
- Submit housing application by July 1 (Fall) or December 1 (Spring)
- Priority given to international and out-of-state students
- Room assignments announced two weeks before semester start''',
        'category': 'Student Life',
        'keywords': 'housing, dormitory, accommodation, residence, rooms, facilities, costs',
        'source': 'Housing Office'
    },
    {
        'title': 'Student Clubs and Organizations',
        'content': '''Zewail City offers various student clubs and organizations:

Technical Clubs:
- Computer Science Society (CSS)
- Robotics Club
- AI and Machine Learning Society
- Cybersecurity Club

Cultural Clubs:
- Drama Society
- Music Club
- Photography Club
- Arts and Culture Committee

Sports Clubs:
- Football team
- Basketball team
- Swimming team
- Fitness and Wellness Club

How to Join:
- Club fair at the beginning of each semester
- Contact club representatives via student portal
- Attend general meetings (schedules posted on bulletin boards)

Starting a New Club:
- Requires minimum 15 interested students
- Submit proposal to Student Affairs Office
- Assign faculty advisor
- Present club objectives and activity plan''',
        'category': 'Student Life',
        'keywords': 'clubs, organizations, extracurricular, activities, sports, societies',
        'source': 'Student Affairs Office'
    },
    
    # Technology & Systems
    {
        'title': 'Student Portal and Online Services',
        'content': '''Access various services through the student portal (portal.zewailcity.edu.eg):

Available Services:
- Course registration
- Grade viewing
- Academic transcript download
- Schedule management
- Financial aid status
- Library resources access
- Email (@student.zewailcity.edu.eg)

Login Credentials:
- Username: Student ID number
- Initial Password: Sent to registered email
- Must change password on first login

Technical Support:
- Email: itsupport@zewailcity.edu.eg
- Phone: ext. 3000
- Help Desk: Building B, Ground Floor
- Hours: Sunday-Thursday, 9:00 AM - 5:00 PM

Two-factor authentication is required for all portal access for security.''',
        'category': 'Technology',
        'keywords': 'portal, online, student portal, login, password, services, IT, support',
        'source': 'IT Services Department'
    },
    {
        'title': 'WiFi and Network Access',
        'content': '''Campus-wide WiFi is available to all students:

Network Details:
- Network Name (SSID): ZewailCity-Student
- Authentication: Student ID and password
- Coverage: All academic buildings, library, dormitories, and common areas

Connection Instructions:
1. Select "ZewailCity-Student" network
2. Enter student ID as username
3. Enter portal password
4. Accept terms and conditions

Network Policies:
- Maximum 3 devices per student
- Bandwidth: 100 Mbps per user
- Prohibited: Torrenting, illegal downloads, unauthorized server hosting
- Violations may result in network access suspension

For connectivity issues:
- Restart your device
- Forget and reconnect to network
- Contact IT support if problem persists''',
        'category': 'Technology',
        'keywords': 'wifi, network, internet, connection, access, IT, connectivity',
        'source': 'IT Services Department'
    },
    
    # Financial Information
    {
        'title': 'Tuition and Fees Structure',
        'content': '''Tuition and fees for the academic year:

Undergraduate Tuition:
- Per Credit Hour: 1,200 EGP
- Full-time (12-18 credits): 18,000 EGP per semester
- Overload (>18 credits): Additional 1,200 EGP per credit

Additional Fees:
- Registration Fee: 500 EGP per semester
- Lab Fees: 300 EGP per lab course
- Health Insurance: 1,000 EGP per year
- Student Activities Fee: 400 EGP per semester

Payment Deadlines:
- Fall Semester: September 15
- Spring Semester: February 15
- Late Payment Penalty: 500 EGP

Payment Methods:
- Bank transfer
- Credit/debit card via student portal
- Payment plans available (contact Financial Aid Office)''',
        'category': 'Financial',
        'keywords': 'tuition, fees, payment, costs, credit hour, financial, money',
        'source': 'Financial Services Office'
    },
    {
        'title': 'Financial Aid and Scholarships',
        'content': '''Financial aid options available to students:

Merit-Based Scholarships:
- Presidential Scholarship: Full tuition (GPA 3.8+)
- Dean\'s Scholarship: 50% tuition (GPA 3.5-3.79)
- Academic Excellence: 25% tuition (GPA 3.0-3.49)

Need-Based Aid:
- Application required (FAFSA or equivalent)
- Based on family income and financial need
- Covers 20-100% of tuition
- Requires annual renewal

Work-Study Program:
- Part-time employment on campus (10-15 hours/week)
- Hourly wage: 50 EGP
- Positions in library, labs, administrative offices
- Apply through student portal

Application Process:
- Submit financial aid application by June 1
- Provide required financial documents
- Awards announced by July 15
- Contact: finaid@zewailcity.edu.eg''',
        'category': 'Financial',
        'keywords': 'financial aid, scholarships, funding, grants, work study, tuition assistance',
        'source': 'Financial Aid Office'
    },
]


def populate_knowledge_base():
    """Populate the knowledge base with sample data"""
    try:
        # Get repository
        kb_repo = RepositoryFactory.get_repository('knowledge_base')
        
        # Create table if not exists
        kb_repo.create_table()
        
        # Check if data already exists
        existing_docs = kb_repo.get_all()
        if len(existing_docs) > 0:
            print(f"Knowledge base already contains {len(existing_docs)} documents.")
            response = input("Do you want to clear existing data and repopulate? (yes/no): ")
            if response.lower() != 'yes':
                print("Keeping existing data.")
                return
            else:
                print("Clearing existing data...")
                # Note: You might want to add a clear_all method to the repository
        
        # Add sample data
        print(f"Adding {len(SAMPLE_DATA)} documents to knowledge base...")
        
        success_count = 0
        for data in SAMPLE_DATA:
            try:
                kb = KnowledgeBase(
                    title=data['title'],
                    content=data['content'],
                    category=data['category'],
                    keywords=data['keywords'],
                    source=data['source']
                )
                kb_repo.add(kb)
                success_count += 1
                print(f"[+] Added: {data['title']}")
            except Exception as e:
                print(f"[-] Failed to add {data['title']}: {e}")
        
        print(f"\nSuccessfully added {success_count}/{len(SAMPLE_DATA)} documents!")
        print("\nKnowledge base is now ready for use with the AI Assistant.")
        
    except Exception as e:
        print(f"Error populating knowledge base: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    print("=" * 60)
    print("Knowledge Base Population Script")
    print("=" * 60)
    print("\nThis script will populate the AI Assistant knowledge base")
    print("with sample university information.\n")
    
    populate_knowledge_base()
