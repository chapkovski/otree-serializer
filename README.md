# An example of JSON serializer for oTree models

Most of the action happens in `serializers.py`. We define there
a `Session` serializer which in its turn calls the `Participant`
serializer, which calls `Player` - for each app.

The `Session` serializer also adds the `Subsession` for each app,
and from there a nested serializer for `Group` is called. 

All fields added to the models are automatically added to the
final JSON response (with the exception of fields explicitely
filtered out by `block_fields` list in `serializers`).