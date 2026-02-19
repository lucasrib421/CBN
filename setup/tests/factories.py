import factory
from django.contrib.auth.models import User

from accounts.models import Author, Role
from content.models import Category, Post, PostStatus, Tag
from home.models import HomeSection, HomeSectionItem
from media_app.models import Media
from navigation.models import Menu, MenuItem, Redirect


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda o: f'{o.username}@example.com')


class MediaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Media

    file = factory.django.FileField(filename='image.jpg')
    title = factory.Sequence(lambda n: f'Mídia {n}')
    alt_text = factory.Faker('sentence', nb_words=4)
    image_type = 'IMAGE'


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f'Categoria {n}')
    slug = factory.Sequence(lambda n: f'categoria-{n}')
    color = '#DC2626'
    is_active = True


class TagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tag

    name = factory.Sequence(lambda n: f'Tag {n}')
    slug = factory.Sequence(lambda n: f'tag-{n}')


class RoleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Role

    name = factory.Sequence(lambda n: f'Role {n}')
    slug = factory.Sequence(lambda n: f'role-{n}')
    description = factory.Faker('sentence')


class AuthorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Author

    user = factory.SubFactory(UserFactory)
    keycloak_id = factory.Faker('uuid4')
    name = factory.Faker('name')
    bio = factory.Faker('paragraph')
    avatar = factory.SubFactory(MediaFactory)
    role = factory.SubFactory(RoleFactory)


class PostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Post

    title = factory.Sequence(lambda n: f'Post {n}')
    subtitle = factory.Faker('sentence')
    slug = factory.Sequence(lambda n: f'post-{n}')
    content = factory.Faker('text', max_nb_chars=500)
    cover_image = factory.SubFactory(MediaFactory)
    author = factory.SubFactory(AuthorFactory)
    status = PostStatus.PUBLISHED

    @factory.post_generation
    def categories(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for category in extracted:
                self.categories.add(category)
        else:
            self.categories.add(CategoryFactory())

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for tag in extracted:
                self.tags.add(tag)


class HomeSectionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = HomeSection

    title = factory.Sequence(lambda n: f'Seção {n}')
    section_type = 'HIGHLIGHTS'
    order = factory.Sequence(lambda n: n + 1)
    is_active = True


class HomeSectionItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = HomeSectionItem

    section = factory.SubFactory(HomeSectionFactory)
    post = factory.SubFactory(PostFactory)
    order = factory.Sequence(lambda n: n + 1)


class MenuFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Menu

    title = factory.Sequence(lambda n: f'Menu {n}')
    slug = factory.Sequence(lambda n: f'menu-{n}')
    is_active = True


class MenuItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MenuItem

    menu = factory.SubFactory(MenuFactory)
    parent = None
    label = factory.Sequence(lambda n: f'Item {n}')
    url = factory.Sequence(lambda n: f'/item-{n}')
    order = factory.Sequence(lambda n: n + 1)
    target = '_self'
    is_active = True


class RedirectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Redirect

    old_path = factory.Sequence(lambda n: f'/old-{n}')
    new_path = factory.Sequence(lambda n: f'/new-{n}')
    url_type = 'permanent'
    is_active = True
