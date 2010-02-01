Guidelines
==========

Some important things to remind:

* We adhere to the KISS (keep it simple, stupid) principle. If you
  find that something could be done simpler, fix it. We consider
  excessive complexity a bug.
* All data validation should be done in the XMLRPC server, not here.
  Server must do validation anyway, and there's no reason to do it
  twice.
