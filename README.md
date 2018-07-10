A demo app for testing Sqreen webhooks.

# Dependencies

Assuming a homebrew + pyenv environment:

    brew install pyenv openssl readline xz

Using python 3.6.4:

    pyenv install 3.6.4
    pyenv local 3.6.4

Python dependencies are stored in the requirements.txt file. Install with:

    pip install -r requirements.txt

# Running

- use the `rundev.sh` script to run the flask application in development mode.
- use the `test.sh` script to run the tests.

To trigger a Sqreen webhook invocation:

    # This assumes that network scanner protection is enabled in
    # the Sqreen dashboard. This request pretends to be the 'Arachni' scanner
    curl -A 'Arachni/v1.3' http://localhost:5000

# Description

There are 2 solutions, identified with the tags 'v1' and 'v2-abstractbaseclass'. The first version
uses an informal interface for the dispatcher backends, whereas v2 uses abstract base classes.

- The application exposes an endpoint that Sqreen can post its payload to (/sqreenhook).
- The endpoint has a decorator, which is responsible for validating the incoming payload's signature.
  If the signature is invalid, the request is aborted with status code 400.
- If the signature is valid, the payload is deserialized from JSON, and handed to the Dispatcher class.
- the dispatcher package contains the Dispatcher class and a dispatcher.backends subpackage.
  - the Dispatcher class is responsible for forwarding the deserialized payload to each backend.
  - (in the 'v1' version) each backend registers itself with the Dispatcher class by using the @Dispatcher.backend decorator on itself.
    - this results in a Dispatcher.BACKENDS array being populated by backend types. Whenever a Sqreen payload is being
      processed, each type from Dispatcher.BACKENDS will be instantiated, assigned a logger, and asked to process the payload.
  - (in the 'v2' version) the default backends are discovered simply as AbstractBaseClass child classes
- there are 2 backends included by default:
  - a Slack backend
    - this backend POSTs the humanized_description of each Sqreen event to Slack.
  - a logger backend
    - this backend outputs the humanized_description of each Sqreen event to the logger (as an info message).
- there is no explicit support for enabling/disabling of backends. Instead:
  - some backends (e.g. Slack) may output a warning and not perform any work until it has the required configuration (and thus being implicitly enabled)
  - some backends (e.g. Logger) work always, and can be removed by manipulating the Dispatcher.BACKENDS (or Dispatcher.ENABLED_BACKENDS in v2) class variable.

## Differences in nomenclature between v1 and v2

- in v1 the enabled backend classes are stored in Dispatcher.BACKENDS
- in v2 the enabled backend classes are stored in Dispatcher.ENABLED_BACKENDS

# Configuration

All of the configuration happens via environment variables (using the `.env` file is supported as well).

There are two mandatory configuration values:

- `SQREEN_WEBHOOK_SECRET` - set this to the secret value configured in the Sqreen dashboard for the webhook. This
  value is used to determine if the incoming payload is correctly signed.
- `SQREEN_TOKEN` - set this to your Sqreen API token. This is required by the Sqreen library.

Optional configuration:

- `BACKEND_SLACK_URL` - the URL to which the Slack backend should post its data. If this environment variable is not present,
  the Slack backend will not do anything (apart from logging a warning).

## Example .env file

    $ cat .env
    SQREEN_WEBHOOK_SECRET=abc...xyz
    SQREEN_TOKEN=38cc5939802....dc1377d
    BACKEND_SLACK_URL=https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX

# Troubleshooting

## ModuleNotFoundError when running pytest

This happens because tests are in an external directory from the rest of the application, and need access
to the application code.

The application code is included in the "app" package, but for it to be importable, the correct path needs to
be set first.

Instead of running pytest directly, use the test.sh script. It invokes pytest in a way that allows
importing the "app" module.

## zipimport.ZipImportError: can't decompress data; zlib not available

    brew install readline xz
    export LDFLAGS="-L$(brew --prefix zlib)/lib"
    export CFLAGS="-I$(brew --prefix zlib)/include"

