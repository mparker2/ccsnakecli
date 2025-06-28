rule touch_output:
    output:
        config["outfile"]
    shell:
        "touch {output}"