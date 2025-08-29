from django.core.management.base import BaseCommand
from library.models import Book
from django.core.files.base import ContentFile

class Command(BaseCommand):
    help = 'Add sample books to the database'

    def handle(self, *args, **kwargs):
        books = [
            {
                'title': 'The Great Gatsby',
                'author': 'F. Scott Fitzgerald',
                'description': 'A classic novel set in the Roaring Twenties.',
                'pdf_content': b'This is a sample PDF for The Great Gatsby.'
            },
            {
                'title': 'To Kill a Mockingbird',
                'author': 'Harper Lee',
                'description': 'A novel about racial injustice in the Deep South.',
                'pdf_content': b'This is a sample PDF for To Kill a Mockingbird.'
            },
            {
                'title': '1984',
                'author': 'George Orwell',
                'description': 'A dystopian novel about totalitarianism.',
                'pdf_content': b'This is a sample PDF for 1984.'
            },
            {
                'title': 'Pride and Prejudice',
                'author': 'Jane Austen',
                'description': 'A romantic novel of manners in Georgian-era England.',
                'pdf_content': b'This is a sample PDF for Pride and Prejudice.'
            },
            {
                'title': 'The Hobbit',
                'author': 'J.R.R. Tolkien',
                'description': 'A fantasy novel about Bilbo Baggins and his journey.',
                'pdf_content': b'This is a sample PDF for The Hobbit.'
            },
            {
                'title': 'The Catcher in the Rye',
                'author': 'J.D. Salinger',
                'description': 'A novel about teenage alienation and loss of innocence.',
                'pdf_content': b'This is a sample PDF for The Catcher in the Rye.'
            },
            {
                'title': 'Lord of the Flies',
                'author': 'William Golding',
                'description': 'A novel about the dark side of human nature.',
                'pdf_content': b'This is a sample PDF for Lord of the Flies.'
            },
            {
                'title': 'Animal Farm',
                'author': 'George Orwell',
                'description': 'An allegorical novella about the Russian Revolution.',
                'pdf_content': b'This is a sample PDF for Animal Farm.'
            },
        ]
        for book in books:
            b = Book(title=book['title'], author=book['author'], description=book['description'])
            b.pdf.save(f"{book['title'].replace(' ', '_')}.pdf", ContentFile(book['pdf_content']))
            b.save()
        self.stdout.write(self.style.SUCCESS('Sample books added successfully.')) 