from books.models import book
book1 = book(name='Clean Code: A Handbook of Agile Software Craftsmanship',description='My fav book',author='Roberr C Martin',price=35.99)
book2 = book(name='Code Complete: A Practical Handbook of Software Construction',description='One of the best practical guides to programming',author='Steve McConnell',price=54.99)
book3 = book(name='Head First Software Architecture: A Learners Guide to Architectural Thinking',description='Teaches software architecture ',author='Raju Gandhi',price=505.99)
book4 = book(name='The Warren Buffett Way',description='An insightful new take on the life and work of one of the worlds most remarkable investors',author='Robert G. Hagstrom',price=54.99)
book1.save()
book2.save()
book3.save()
book4.save()
quit()