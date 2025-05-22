import pusher

# pusher configuration
pusher_client = pusher.Pusher(
    app_id="1980276",
    key="682407f9d91aaf86de6f",
    secret="aefab4c4834cff4aaf9a",
    cluster="eu",
    ssl=True,
)
# example
# pusher_client.trigger('my-channel', 'my-event', {'message': 'hello world'})