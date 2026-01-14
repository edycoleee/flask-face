from run import create_app

def test_get_halo():
    app = create_app()
    client = app.test_client()

    res = client.get("/api/halo/")
    assert res.status_code == 200
    assert res.json["status"] == "success"

def test_post_halo():
    app = create_app()
    client = app.test_client()

    payload = {"nama": "edy", "message": "Post Halo"}
    res = client.post("/api/halo/", json=payload)

    assert res.status_code == 200
    assert res.json["data"]["nama"] == "edy"
