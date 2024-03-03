from flask import Flask, request, render_template_string

app = Flask(__name__)

# HTML模板，包含一个简单的表单
HTML_TEMPLATE = '''
<!doctype html>
<html lang="en">
<head>
  <title>Calculator</title>
</head>
<body>
  <h1>Simple Calculator</h1>
  <form method="post">
    <input type="number" name="num1" placeholder="Number 1" required>
    <input type="number" name="num2" placeholder="Number 2" required>
    <button type="submit">Calculate</button>
  </form>
  {% if result is not none %}
    <h2>Result: {{ result }}</h2>
  {% endif %}
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def calculate():
    result = None
    if request.method == 'POST':
        # 从表单获取数字
        num1 = request.form.get('num1', type=int)
        num2 = request.form.get('num2', type=int)
        # 计算结果
        result = num1 + num2
    # 渲染HTML模板
    return render_template_string(HTML_TEMPLATE, result=result)


if __name__ == '__main__':
    app.run(debug=True,port=8080,host='0.0.0.0')