from django.test import SimpleTestCase

from main.templatetags.custom_filters import safe_map_iframe, sanitize_html


class SanitizedHTMLFilterTests(SimpleTestCase):
    def test_removes_scripts_and_dangerous_links(self):
        html = '<p>Hello</p><script>alert(1)</script><a href="javascript:alert(1)">bad</a>'

        rendered = str(sanitize_html(html))

        self.assertIn('<p>Hello</p>', rendered)
        self.assertNotIn('<script', rendered)
        self.assertNotIn('alert(1)', rendered)
        self.assertNotIn('javascript:', rendered)

    def test_keeps_safe_relative_links(self):
        html = '<a href="/articles/" target="_blank">Articles</a>'

        rendered = str(sanitize_html(html))

        self.assertIn('href="/articles/"', rendered)
        self.assertIn('target="_blank"', rendered)
        self.assertIn('rel="noopener noreferrer"', rendered)


class SafeMapIframeFilterTests(SimpleTestCase):
    def test_allows_google_maps_iframe_and_drops_extra_attributes(self):
        iframe = (
            '<iframe src="https://www.google.com/maps/embed?pb=test" '
            'onload="alert(1)" allowfullscreen></iframe>'
        )

        rendered = str(safe_map_iframe(iframe))

        self.assertIn('src="https://www.google.com/maps/embed?pb=test"', rendered)
        self.assertIn('allowfullscreen', rendered)
        self.assertNotIn('onload', rendered)

    def test_drops_non_google_maps_iframe(self):
        iframe = '<iframe src="https://example.com/maps/embed"></iframe>'

        self.assertEqual(str(safe_map_iframe(iframe)), '')
