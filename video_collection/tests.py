from django.test import TestCase
from django.urls import reverse
from .models import Video
from django.core.exceptions import ValidationError
from django.db import IntegrityError

# Create your tests here.
class TestHomePageMessage(TestCase):

    def test_app_title_message_shown_on_home_page(self):
        url = reverse('home')
        response = self.client.get(url)
        self.assertContains(response, 'Hydraulic Compressor')
    

class TestAddVideos(TestCase):
    
    def test_add_video(self):

        valid_video = {
            'name': 'lego',
            'url': 'https://www.youtube.com/watch?v=S_t8CySI-Uw',
            'notes': 'Legos getting the smush from the press'
        }

        url = reverse('add_video')
        response = self.client.post(url, data=valid_video, follow=True)

        self.assertTemplateUsed('video_collection/video_list.html')
        
        # does the video list show the new video?
        self.assertContains(response, 'Lego')
        self.assertContains(response, 'Legos getting the smush from the press')
        self.assertContains(response, 'https://www.youtube.com/watch?v=S_t8CySI-Uw')

        video_count = Video.objects.count()
        self.assertEqual(1, video_count)

        video = Video.objects.first()

        self.assertEqual('lego', video.name)
        self.assertEqual('https://www.youtube.com/watch?v=S_t8CySI-Uw', video.url)
        self.assertEqual('Legos getting the smush from the press', video.notes)
        self.assertEqual('S_t8CySI-Uw', video.video_id)
    
    def test_add_invalid_url_video_not_added(self):

        invalid_video_urls = [
            'https://www.youtube.com/watch',
            'https://www.youtube.com/watch?',
            'https://www.youtube.com/watch?abc=1234',
            'https://www.youtube.com/watch?v=',
            'https://www.github.com/',
            'https://www.facebook.com',
            'https://www.facebook.com?v=56789'
        ]

        for invalid_video_url in invalid_video_urls:

            new_video = {
                'name': 'example',
                'url': invalid_video_url,
                'notes': 'example notes'
            }

            url = reverse('add_video')
            response = self.client.post(url, new_video)
            
            self.assertTemplateNotUsed('video_collection/add.html')

            messages = response.context['messages']
            message_texts = [ message.message for message in messages ]

            self.assertIn('Invalid YouTube URL', message_texts)
            self.assertIn('Please check the info entered.', message_texts)

            video_count = Video.objects.count()
            self.assertEqual(0, video_count)

class TestVideoDetail(TestCase):

    def test_video_detail_page_shows_all_info(self):
        # test adapted from wishlist test_place_detail
        v1 = Video.objects.create(name='Blahblah', notes='qwerty1234', url='https://www.youtube.com/watch?v=1234')
        response = self.client.get(reverse('video_detail', kwargs={'video_pk':1} ))
        # Check correct template was used
        self.assertTemplateUsed(response, 'video_collection/video_detail.html')

        # What data was sent to the template?
        data_rendered = response.context['video']

        # Same as data sent to template?
        self.assertEqual(data_rendered, v1)

        # and correct data shown on page?
    
        self.assertContains(response, 'Blahblah') 
        self.assertContains(response, 'qwerty1234')  
        self.assertContains(response, 'https://www.youtube.com/watch?v=1234') 

class TestVideoList(TestCase):
    
    def test_all_videos_displayed_in_correct_order(self):

        v1 = Video.objects.create(name='abc', notes='example', url='https://www.youtube.com/watch?v=1234')
        v2 = Video.objects.create(name='YUZ', notes='example', url='https://www.youtube.com/watch?v=1235')
        v3 = Video.objects.create(name='AAA', notes='example', url='https://www.youtube.com/watch?v=1236')
        v4 = Video.objects.create(name='klm', notes='example', url='https://www.youtube.com/watch?v=1237')

        expected_video_order = [ v3, v1, v4, v2 ]

        url = reverse('video_list')
        response = self.client.get(url)

        videos_in_template = list(response.context['videos'])

        self.assertEqual(videos_in_template, expected_video_order)

    def test_no_video_message(self):

        url = reverse('video_list')
        response = self.client.get(url)
        self.assertContains(response, 'No matching videos')
        self.assertEqual(0, len(response.context['videos']))

    def test_video_number_message_one_video(self):
        v1 = Video.objects.create(name='abc', notes='example', url='https://www.youtube.com/watch?v=1234')
        url = reverse('video_list')
        response = self.client.get(url)
        self.assertContains(response, '1 Video')
        self.assertNotContains(response, '1 Videos')

    def test_video_number_message_two_videos(self):
        v1 = Video.objects.create(name='abc', notes='example', url='https://www.youtube.com/watch?v=1234')
        v2 = Video.objects.create(name='abc', notes='example', url='https://www.youtube.com/watch?v=1235')
        url = reverse('video_list')
        response = self.client.get(url)
        self.assertContains(response, '2 Videos')

class TestVideoSearch(TestCase):

    def test_video_search_matches(self):
        v1 = Video.objects.create(name='ABC', notes='example', url='https://www.youtube.com/watch?v=456')
        v2 = Video.objects.create(name='nope', notes='example', url='https://www.youtube.com/watch?v=789')
        v3 = Video.objects.create(name='abc', notes='example', url='https://www.youtube.com/watch?v=123')
        v4 = Video.objects.create(name='hello aBc!!!', notes='example', url='https://www.youtube.com/watch?v=101')
        
        expected_video_order = [v1, v3, v4]
        response = self.client.get(reverse('video_list') + '?search_term=abc')
        videos_in_template = list(response.context['videos'])
        self.assertEqual(expected_video_order, videos_in_template)


    def test_video_search_no_matches(self):
        v1 = Video.objects.create(name='ABC', notes='example', url='https://www.youtube.com/watch?v=456')
        v2 = Video.objects.create(name='nope', notes='example', url='https://www.youtube.com/watch?v=789')
        v3 = Video.objects.create(name='abc', notes='example', url='https://www.youtube.com/watch?v=123')
        v4 = Video.objects.create(name='hello aBc!!!', notes='example', url='https://www.youtube.com/watch?v=101')
        
        expected_video_order = []  # empty list 
        response = self.client.get(reverse('video_list') + '?search_term=kittens')
        videos_in_template = list(response.context['videos'])
        self.assertEqual(expected_video_order, videos_in_template)
        self.assertContains(response, 'No matching videos')

class TestVideoModel(TestCase):
    
    def test_invalid_url_raises_validation_error(self):
        invalid_video_urls = [
            'https://www.youtube.com/watch',
            'https://www.youtube.com/watch/somethingelse/',
            'https://www.youtube.com/watch/somethingelse?v=12345',
            'http://www.youtube.com/watch/somethingelse?v=12345',
            'https://www.youtube.com/watch?',
            'https://www.youtube.com/watch?abc=1234',
            'hhhhhhhhhhhasdasd1234r5',
            'jhjhjhjhjhhttps://www.youtube.com/watch?abc=1234',
            'https://www.youtube.com/watch?v=',
            'https://www.github.com/',
            'https://www.facebook.com',
            'https://www.facebook.com?v=56789'
        ]

        for invalid_video_url in invalid_video_urls:

            with self.assertRaises(ValidationError):
                Video.objects.create(name= 'example', url= invalid_video_url, notes= 'example notes')
                
        self.assertEqual(0, Video.objects.count())

    def test_duplicate_video_raises_integrity_error(self):
        v1 = Video.objects.create(name='ABC', notes='example', url='https://www.youtube.com/watch?v=456')
        with self.assertRaises(IntegrityError):
            Video.objects.create(name='ABC', notes='example', url='https://www.youtube.com/watch?v=456')
    
