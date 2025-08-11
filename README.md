# Hospital Management System

A comprehensive Django-based hospital management system that streamlines hospital operations including patient management, appointment scheduling, billing, medical records, and more.

## Demo

Check out the demo video to see the system in action:

[![Hospital Management System Demo](https://img.youtube.com/vi/demo/0.jpg)](https://www.tiktok.com/@rashidshafique.09/video/7530213181197716743)

## Features

- **Patient Management**: Complete patient registration, profiles, and medical history tracking
- **Doctor Management**: Doctor profiles, specializations, and availability scheduling
- **Appointment Scheduling**: Online appointment booking with calendar integration
- **Billing System**: Invoice generation, payment processing, and financial tracking
- **Medical Records**: Digital storage and management of patient medical records
- **Analytics Dashboard**: Real-time insights into hospital operations and performance metrics
- **Notification System**: Automated alerts and notifications for appointments, payments, and updates
- **User Authentication**: Secure login system with role-based access control
- **Responsive Design**: Mobile-friendly interface that works on all devices

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd hospital-management-system
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up the database:
   ```bash
   python manage.py migrate
   ```

5. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

6. Run the development server:
   ```bash
   python manage.py runserver
   ```

## Usage

1. Access the admin panel at `http://127.0.0.1:8000/admin/` to manage hospital data
2. Register new users at `http://127.0.0.1:8000/register/`
3. Login at `http://127.0.0.1:8000/login/` to access the dashboard
4. Navigate through the different modules using the sidebar menu

## Technologies Used

- **Backend**: Django, Python
- **Database**: SQLite (default), with support for PostgreSQL/MySQL
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **API**: Django REST Framework for API endpoints
- **Authentication**: Django's built-in authentication system
- **Static Files**: Django's static files handling
- **Deployment**: Ready for deployment on platforms like Heroku, AWS, or DigitalOcean

## Modules

- **Core**: Main application with user profiles and dashboard
- **Patients**: Patient registration and management
- **Doctors**: Doctor profiles and availability
- **Appointments**: Scheduling and appointment management
- **Billing**: Invoice generation and payment processing
- **Medical Records**: Digital storage of patient records
- **Analytics**: Data visualization and reporting
- **Notifications**: Alert system for hospital events
- **API**: RESTful API endpoints for external integrations

## Contributing

1. Fork the repository
2. Create a new branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For support or inquiries, please contact the development team.
