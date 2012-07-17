%include menu.tpl
<div class="row-fluid">
    <div class="span6">
        <div class="well">
            %if defined("error") and error.status:
            <h1>Error {{error.status}}</h1>
            %elif defined("error") and error.exception:
            <h1>{{error.exception}}</h1>
            %else:
            <h1>Error</h1>
            %end
            %if defined("msg"):
            <h2>{{msg}}</h2>
            %end
        </div>
        %if defined("error") and error.output:
        <div class="row-fluid">
            <div class="alert alert-error">
                {{error.output}}
            </div>
        </div>
        %end
        %if defined("error") and error.traceback:
        <div class="row-fluid">
            <div class="alert alert-error">
                {{error.traceback}}
            </div>
        </div>
        %end
    </div>
    <div class="span6">
        %if defined("img"):
        <img src="{{img}}"  class="thumbnail"/>
        %else:
        <img src="/static/img/2001.gif"  class="thumbnail"/>
        %end
    </div>

</div>
<div class="row-fluid">
   <a class="btn btn-large btn-danger" href="/">Life must go on</a>
</div>

%rebase boilerplate title = "MicroPsi Error"
