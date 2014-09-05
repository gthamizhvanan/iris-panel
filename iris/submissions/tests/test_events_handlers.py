#pylint: skip-file
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from iris.core.models import (
    Domain, SubDomain, GitTree, Product,
    Submission,
    )


class EventHandlerTest(TestCase):

    fixtures = ['users', 'domains', 'subdomains', 'gittrees', 'products', 'submissions']

    def login(self, user='robot', pwd='robot'):
        assert self.client.login(username=user, password=pwd)

    def test_post_required(self):
        url = reverse('event_submitted')
        self.login()
        r = self.client.get(url)
        self.assertEquals(405, r.status_code)

    def test_login_required(self):
        url = reverse('event_submitted')
        r = self.client.post(url)
        self.assertEquals(403, r.status_code)

    def test_permission_required(self):
        url = reverse('event_submitted')
        self.login('alice', 'alice')
        r = self.client.post(url, {
                'gitpath': 'framework/system/dlog',
                'tag': 'submit/trunk/yyyy-mm-dd',
                'commit_id': 'sha1',
                'submitter_email': 'someone@localhost',
                })
        self.assertEquals(403, r.status_code)

    def test_missing_parameter(self):
        url = reverse('event_submitted')
        self.login()
        r = self.client.post(url)
        self.assertEquals(406, r.status_code)

    def test_submitted(self):
        self.login()
        r = self.client.post(reverse('event_submitted'), {
                'gitpath': 'framework/system/dlog',
                'tag': 'submit/trunk/yyyy-mm-dd',
                'commit_id': 'sha1',
                'submitter_email': 'someone@localhost',
                })
        self.assertEquals(201, r.status_code)
        Submission.objects.get(name='submit/trunk/yyyy-mm-dd')

    def test_pre_created(self):
        self.login()
        r = self.client.post(reverse('event_pre_created'), {
                'gitpath': 'framework/system/dlog',
                'tag': 'submit/trunk/01',
                'product': 'Tizen:IVI',
                'project': 'home:prerelease:tizen:ivi:submit:trunk:01',
                })
        self.assertEquals(201, r.status_code)

    def test_pre_created_bad_submission(self):
        self.login()
        r = self.client.post(reverse('event_pre_created'), {
                'gitpath': 'does/not/exist',
                'tag': 'does/not/exist',
                'product': 'Tizen:IVI',
                'project': 'home:prerelease:tizen:ivi:submit:trunk:01',
                })
        self.assertEquals(406, r.status_code)

    def test_pre_created_bad_product(self):
        self.login()
        r = self.client.post(reverse('event_pre_created'), {
                'gitpath': 'framework/system/dlog',
                'tag': 'submit/trunk/01',
                'product': 'Bad',
                'project': 'home:prerelease:tizen:ivi:submit:trunk:01',
                })
        self.assertEquals(406, r.status_code)

    def test_package_built_succeeded(self):
        self.login()
        r = self.client.post(reverse('event_package_built'), {
                'name': 'dlog',
                'repo': 'standard',
                'arch': 'i586',
                'project': 'home:prerelease:tizen:ivi:submit:trunk:02',
                'status': 'success',
                'url': 'http://url.to.live.repo',
                'log': 'http://url.to.build.log',
                })
        self.assertEquals(200, r.status_code)

    def test_package_built_failed(self):
        self.login()
        r = self.client.post(reverse('event_package_built'), {
                'name': 'dlog',
                'repo': 'standard',
                'arch': 'armv7el',
                'project': 'home:prerelease:tizen:ivi:submit:trunk:02',
                'status': 'failure',
                'url': 'http://url.to.live.repo',
                'log': 'http://url.to.build.log',
                })
        self.assertEquals(200, r.status_code)

    def test_image_building(self):
        self.login()
        r = self.client.post(reverse('event_image_building'), {
                'name': 'ivi-mbr-i586',
                'project': 'home:prerelease:tizen:ivi:submit:trunk:02',
                })
        self.assertEquals(200, r.status_code)

    def test_image_building_bad_project(self):
        self.login()
        r = self.client.post(reverse('event_image_building'), {
                'name': 'ivi-mbr-i586',
                'project': 'doesnotexist',
                })
        self.assertEquals(406, r.status_code)

    def test_image_created(self):
        self.login()
        r = self.client.post(reverse('event_image_created'), {
                'name': 'ivi-mbr-x64',
                'project': 'home:prerelease:tizen:ivi:submit:trunk:02',
                'status': 'success',
                'url': 'http://url.to.image',
                'log': 'http://url.to.image.log',
                })
        self.assertEquals(200, r.status_code)

    def test_image_created_image_doesnot_exist(self):
        self.login()
        r = self.client.post(reverse('event_image_created'), {
                'name': 'ivi-mbr-i586',
                'project': 'home:prerelease:tizen:ivi:submit:trunk:02',
                'status': 'success',
                'url': 'http://url.to.image',
                'log': 'http://url.to.image.log',
                })
        self.assertEquals(406, r.status_code)

    def test_image_created_project_doesnot_exist(self):
        self.login()
        r = self.client.post(reverse('event_image_created'), {
                'name': 'ivi-mbr-i586',
                'project': 'doesnt exist',
                'status': 'success',
                'url': 'http://url.to.image',
                'log': 'http://url.to.image.log',
                })
        self.assertEquals(406, r.status_code)

    def test_repa_accepted(self):
        self.login()
        r = self.client.post(reverse('event_repa_action'), {
                'project': 'home:prerelease:tizen:ivi:submit:trunk:02',
                'status': 'accepted',
                'who': 'someone@tizen.org',
                'reason': 'Good!',
                })
        self.assertEquals(200, r.status_code)

    def test_repa_rejected(self):
        self.login()
        r = self.client.post(reverse('event_repa_action'), {
                'project': 'home:prerelease:tizen:ivi:submit:trunk:02',
                'status': 'rejected',
                'who': 'someone@tizen.org',
                'reason': "Errors found in QA tests",
                })
        self.assertEquals(200, r.status_code)