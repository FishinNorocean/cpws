def format_output(output):
    try:
        #additional_note_start = output.rfind("|")
        #additional_note = output[additional_note_start+1:].strip()

        lines = output.split("\n")
        if len(lines) < 3: 
            return "Not enough data provided"
        data = lines[2].split("|")
        if len(data) < 6: 
            return "Not enough data provided"

        plaintiff = data[1].strip()
        plaintiff_gender = data[2].strip()
        defendants = data[3].strip()
        defendant_gender = data[4].strip()
        verdict = data[5].strip() if len(data) > 5 else "Data not provided"

        return plaintiff, plaintiff_gender, defendants, defendant_gender, verdict
    except Exception as e:
        return str(e)