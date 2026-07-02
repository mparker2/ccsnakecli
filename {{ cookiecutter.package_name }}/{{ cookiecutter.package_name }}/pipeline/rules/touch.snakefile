rule touch_output:
    output:
        cfg.target_file
    shell:
        "touch {output}"