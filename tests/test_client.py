import multiprocessing
import os
import unittest
import client.file_utils as file_utils
import client.call_endpoints as endpoints

user_name = "new user"
password = "password123"
project_name = "project"
user_2 = "new user 2"


class MyTestCase(unittest.TestCase):

    # def test_compress_decompress(self):
    #     save_path = "tests\\data_save_test\\"
    #     folder_name = "compression_test\\"
    #     original_path = f"tests\\{folder_name}"
    #
    #     data = file_utils.compress_and_encode(original_path)
    #     file_utils.save_commit_from_data(data, save_path)
    #
    #     files = os.listdir(original_path)
    #     for file in files:
    #         f = open(f"{save_path}{folder_name}{file}", "rb")
    #         s_decoded = f.read()
    #         f.close()
    #         f = open(f"{original_path}{file}", "rb")
    #         s_original = f.read()
    #         f.close()
    #         self.assertEqual(s_original, s_decoded)
    #
    #     # if this fails try to recompile test_binary.exe to your machine
    #     os.system(f"{save_path}{folder_name}test_binary.exe")

    def test_endpoints(self):
        # test sign up
        try:
            ok, session_id = endpoints.login(user_name=user_name, password=password)
            endpoints.delete_user(session_id)
        except:
            pass
        try:
            ok, session_id = endpoints.login(user_name=user_2, password=password)
            endpoints.delete_user(session_id)
        except:
            pass
        ok, session_id = endpoints.sign_up(user_name, password)
        self.assertTrue(ok)
        ok, error_message = endpoints.sign_up(user_name, password)
        self.assertFalse(ok)

        # test logout
        ok, message = endpoints.logout(session_id)
        self.assertTrue(ok)
        ok, message = endpoints.logout(session_id)
        self.assertFalse(ok)

        # test login
        ok, session_id = endpoints.login(user_name, password)
        self.assertTrue(ok)
        ok, message = endpoints.login(user_name, password)
        self.assertFalse(ok)

        # test delete user
        ok, message = endpoints.delete_user(session_id)
        self.assertTrue(ok)
        ok, session_id = endpoints.sign_up(user_name, password)

        # test add project
        ok, message = endpoints.add_project(session_id, project_name, "description")
        self.assertTrue(ok)
        ok, message = endpoints.add_project(session_id, project_name, "description")
        self.assertFalse(ok)

        # test delete project
        ok, message = endpoints.delete_project(session_id, project_name)
        self.assertTrue(ok)
        ok, message = endpoints.delete_project(session_id, project_name)
        self.assertFalse(ok)
        endpoints.add_project(session_id, project_name, "description")

        # test get project info
        ok, message = endpoints.get_project_info(session_id, project_name, user_name)
        self.assertTrue(ok)
        ok, message = endpoints.get_project_info(session_id, project_name, user_2)
        self.assertFalse(ok)

        # test update project sharing
        ok, message = endpoints.update_project_sharing(session_id, project_name, user_2, True)
        self.assertFalse(ok)
        _, session_id_2 = endpoints.sign_up(user_2, password)
        ok, message = endpoints.update_project_sharing(session_id, project_name, user_2, True)
        self.assertTrue(ok)
        
        # test commit + permissions
        ok, message = endpoints.commit(session_id_2, project_name, user_name, "new commit", "new commit",
                                       "tests/compression_test")
        self.assertTrue(ok)
        ok, message = endpoints.update_project_sharing(session_id, project_name, user_2, False)
        self.assertTrue(ok)
        ok, message = endpoints.commit(session_id_2, project_name, user_name, "new commit", "new commit",
                                       "tests/compression_test")
        self.assertFalse(ok)

        # test get commit info + permissions
        ok, commit_info = endpoints.get_commit_info(session_id_2, project_name, user_name, 0)
        self.assertTrue(ok)
        ok, commit_info = endpoints.get_commit_info(session_id_2, project_name, user_name, 100)
        self.assertFalse(ok)
        endpoints.update_project_sharing(session_id, project_name, user_2)
        ok, commit_info = endpoints.get_commit_info(session_id_2, project_name, user_name, 0)
        self.assertFalse(ok)

        # test get commit data
        ok, success = endpoints.get_commit_data(session_id, project_name, user_name, 0, "tests/data_save_test")
        self.assertTrue(ok and success)
        ok, message = endpoints.get_commit_data(session_id, project_name, user_name, 100, "tests/data_save_test")
        self.assertFalse(ok)

        # test delete commit
        ok, message = endpoints.delete_commit(session_id, project_name, 0)
        self.assertTrue(ok)
        ok, message = endpoints.delete_commit(session_id, project_name, 100)
        self.assertFalse(ok)

        # test delete user
        ok, message = endpoints.delete_user(session_id_2)
        self.assertTrue(ok)
        ok, message = endpoints.delete_user(session_id_2)
        self.assertFalse(ok)





if __name__ == '__main__':
    # proc = multiprocessing.Process(target=communication_manager.main, args=())
    # proc.start()
    unittest.main()
    # proc.terminate()

