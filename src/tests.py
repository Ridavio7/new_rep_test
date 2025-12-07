import unittest
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import app as tested_app


class FlaskAppTests(unittest.TestCase):

    def setUp(self):
        tested_app.app.config["TESTING"] = True
        self.app = tested_app.app.test_client()

        self.test_data_file = os.path.join(os.path.dirname(__file__), "data.json")
        self.original_data = [{"id": 1, "name": "Original", "age": 99}]
        with open(self.test_data_file, "w", encoding="utf-8") as f:
            json.dump(self.original_data, f, indent=2)

    def tearDown(self):
        with open(self.test_data_file, "w", encoding="utf-8") as f:
            json.dump(self.original_data, f, indent=2)

    def test_hello_endpoint(self):
        r = self.app.get("/")
        self.assertEqual(r.status_code, 200)
        self.assertIn(b"Welcome", r.data)

    def test_get_users(self):
        r = self.app.get("/users")
        self.assertEqual(r.status_code, 200)
        self.assertIsInstance(r.json, list)
        self.assertGreaterEqual(len(r.json), 1)

    def test_add_user_success(self):
        new_user = {"name": "Test User", "age": 20}
        r = self.app.post(
            "/users", content_type="application/json", data=json.dumps(new_user)
        )
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.json["status"], "OK")
        self.assertIn("user", r.json)
        self.assertEqual(r.json["user"]["name"], "Test User")
        self.assertTrue(isinstance(r.json["user"]["id"], int))

    def test_add_user_invalid_name(self):
        invalid_user = {"name": "", "age": 20}
        r = self.app.post(
            "/users", content_type="application/json", data=json.dumps(invalid_user)
        )
        self.assertEqual(r.status_code, 400)
        self.assertIn("error", r.json)

    def test_add_user_invalid_age(self):
        invalid_user = {"name": "Valid Name", "age": "twenty"}
        r = self.app.post(
            "/users", content_type="application/json", data=json.dumps(invalid_user)
        )
        self.assertEqual(r.status_code, 400)
        self.assertIn("error", r.json)

    def test_add_user_no_json(self):
        r = self.app.post("/users", data="not json")
        self.assertEqual(r.status_code, 415)

    def test_get_user_by_id_exists(self):
        r = self.app.get("/users/1")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json["id"], 1)

    def test_get_user_by_id_not_found(self):
        r = self.app.get("/users/999")
        self.assertEqual(r.status_code, 404)
        self.assertIn("error", r.json)

    def test_delete_user_success(self):
        new_user = {"name": "ToDelete", "age": 10}
        add_r = self.app.post(
            "/users", content_type="application/json", data=json.dumps(new_user)
        )
        user_id = add_r.json["user"]["id"]

        del_r = self.app.delete(f"/users/{user_id}")
        self.assertEqual(del_r.status_code, 200)
        self.assertEqual(del_r.json["status"], "OK")
        self.assertEqual(del_r.json["deleted_id"], user_id)

    def test_delete_user_not_found(self):
        r = self.app.delete("/users/999")
        self.assertEqual(r.status_code, 404)
        self.assertIn("error", r.json)


if __name__ == "__main__":
    unittest.main()
