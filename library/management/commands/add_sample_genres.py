from django.core.management.base import BaseCommand
from library.models import Genre

class Command(BaseCommand):
    help = 'Add sample genres to the database'

    def handle(self, *args, **options):
        genres_data = [
            {'name': 'Fiction', 'description': 'Imaginative literature', 'color': '#007bff'},
            {'name': 'Non-Fiction', 'description': 'Factual literature', 'color': '#28a745'},
            {'name': 'Science Fiction', 'description': 'Futuristic and scientific themes', 'color': '#17a2b8'},
            {'name': 'Mystery', 'description': 'Detective and crime stories', 'color': '#6f42c1'},
            {'name': 'Romance', 'description': 'Love and relationship stories', 'color': '#e83e8c'},
            {'name': 'Thriller', 'description': 'Suspense and excitement', 'color': '#dc3545'},
            {'name': 'Biography', 'description': 'Life stories of real people', 'color': '#fd7e14'},
            {'name': 'History', 'description': 'Historical events and periods', 'color': '#20c997'},
            {'name': 'Technology', 'description': 'Computer science and tech', 'color': '#6c757d'},
            {'name': 'Self-Help', 'description': 'Personal development', 'color': '#ffc107'},
            {'name': 'Poetry', 'description': 'Verse and poetic literature', 'color': '#6610f2'},
            {'name': 'Children', 'description': 'Books for young readers', 'color': '#fd7e14'},
        ]

        created_count = 0
        for genre_data in genres_data:
            genre, created = Genre.objects.get_or_create(
                name=genre_data['name'],
                defaults={
                    'description': genre_data['description'],
                    'color': genre_data['color']
                }
            )
            if created:
                created_count += 1
                self.stdout.write(f'Created genre: {genre.name}')

        self.stdout.write(
            self.style.SUCCESS(f'Successfully added {created_count} new genres!')
        ) 