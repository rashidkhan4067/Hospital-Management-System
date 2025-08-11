from django.core.management.base import BaseCommand
from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Test all main URLs to ensure they work properly'

    def handle(self, *args, **options):
        client = Client()
        
        # Test URLs that don't require authentication
        public_urls = [
            '/login/',
            '/test/',
        ]
        
        self.stdout.write(self.style.SUCCESS('Testing public URLs...'))
        for url in public_urls:
            try:
                response = client.get(url)
                if response.status_code == 200:
                    self.stdout.write(f'✅ {url} - OK')
                else:
                    self.stdout.write(f'❌ {url} - Status: {response.status_code}')
            except Exception as e:
                self.stdout.write(f'❌ {url} - Error: {str(e)}')
        
        # Test login functionality
        self.stdout.write(self.style.SUCCESS('\nTesting login functionality...'))
        try:
            admin_user = User.objects.filter(email='admin@premiumhms.com').first()
            if admin_user:
                login_success = client.login(username='admin@premiumhms.com', password='admin123')
                if login_success:
                    self.stdout.write('✅ Login - OK')
                    
                    # Test protected URLs
                    protected_urls = [
                        '/',
                        '/patients/',
                        '/doctors/',
                        '/appointments/',
                        '/billing/',
                    ]
                    
                    self.stdout.write(self.style.SUCCESS('\nTesting protected URLs...'))
                    for url in protected_urls:
                        try:
                            response = client.get(url)
                            if response.status_code == 200:
                                self.stdout.write(f'✅ {url} - OK')
                            else:
                                self.stdout.write(f'❌ {url} - Status: {response.status_code}')
                        except Exception as e:
                            self.stdout.write(f'❌ {url} - Error: {str(e)}')
                else:
                    self.stdout.write('❌ Login failed')
            else:
                self.stdout.write('❌ Admin user not found')
        except Exception as e:
            self.stdout.write(f'❌ Login test error: {str(e)}')
        
        self.stdout.write(self.style.SUCCESS('\n🎉 URL testing completed!'))
