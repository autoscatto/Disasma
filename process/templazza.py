cli_data_template       = '[%08x]%-4s0x%02x'
cli_data_char_template  = '[%08x]%-4s0x%02x ; \'%s\''

html_data_template      = """
    <div class="row">
    <div class="toggle" onclick="sv.viewAs(\'C\', %d, %d)">D  </div>
        <div> [</div><div class="address" id="%08x">%08x</div><div>] </div>
        <div class="operator">%4s</div>
        <div class="constant">%02x</div>
    </div>
    <br/>
"""

html_data_char_template = """
    <div class="row">
    <div class="toggle" onclick="sv.viewAs(\'C\', %d, %d)">D  </div>
        <div> [</div><div class="address" id="%08x">%08x</div><div>] </div>
        <div class="operator">%4s</div>
        <div class="constant">%02x</div>
        <div class="comment"> ; \'%s\'
    </div>
    <br/>
"""

html_code_template      = """
    <div class="row">
        <div class="toggle" onclick="sv.viewAs(\'D\', %d, %d)">C  </div>
        <div> [</div><div class="address" id="%08x">%08x</div><div>] </div>
        <div class="operator">%-8s\t</div>
        %s
        <br/>
    </div>
"""

html_code_op_reg        = '<div class="operand_register">%s</div>'
html_code_op_mem        = '<div>[</div><a href="#%08x"><div class="operand_address">%s0x%x</div></a><div>]</div>'
html_code_op_jimm       = '<a href="#%08x"><div class="operand_address">%s0x%x</div></a>'
html_code_op_imm        = '<div class="operand_immediate">%s0x%x</div>'