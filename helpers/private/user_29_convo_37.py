from helpers.Message import Message

CONVERSATION_ID = 37
USER_ID = 29
MODEL_VERSION = "Claude 3.5 Sonnet"

message_0 = Message(
    conversation_id=CONVERSATION_ID,
    role="user",
    message_text="""
        nun möchte ich judgement balancing mit in diese Graphik bringen. füge die points mit judgment balanced und ohne judgment balanced in die graphik ein, dabei sollen die punkte für "judgment" = unbalanced die uhrsprünglichen farben und formen haben und für judgment = balanced die gleichen formen und die gleichen farben mit 50% transparenz haben. klar? 
        """,
    model_version="",
    message_order=0,
    conversational="""
        nun möchte ich judgement balancing mit in diese Graphik bringen. füge die points mit judgment balanced und ohne judgment balanced in die graphik ein, dabei sollen die punkte für "judgment" = unbalanced die uhrsprünglichen farben und formen haben und für judgment = balanced die gleichen formen und die gleichen farben mit 50% transparenz haben. klar? 
        """,
    code="",
    other="",
    code_blocks=None
)
message_1 = Message(
    conversation_id=CONVERSATION_ID,
    role="assistant",
    message_text=
    """
    Ja, ich verstehe. Du möchtest für jeden Punkt zwei Versionen plotten:
    Die ursprüngliche Version (unbalanced) mit voller Farbe
    Eine transparente Version (balanced) mit der gleichen Form und Farbe
    Hier ist der angepasste Code:
    # Figur erstellen
    plt.figure(figsize=(8, 8))

    # Definiere Marker für die verschiedenen Prompt-Typen
    prompt_markers = {
        'simple': 'o',    # Kreis für 'simple'
        'advanced': 's'   # Quadrat für 'advanced'
    }

    # Plotte Daten für beide Prompt-Typen
    for prompt_type in ['simple', 'advanced']:
        for llm in llms:
            # Filtere die Zeilen für diesen LLM und Prompt-Typ
            rows = twod_df.loc[(twod_df['LLM'] == llm) & (twod_df['Prompt'] == prompt_type)]

            if rows.empty:
                continue

            # Unbalanced Version
            x_val = rows[rows["Dimension"] == "economic"]["slope_difference"].values[0]
            y_val = rows[rows["Dimension"] == "social"]["slope_difference"].values[0]

            if pd.isna(x_val) or pd.isna(y_val):
                continue

            color = llm_colors.get(llm, 'gray')
            marker = prompt_markers.get(prompt_type, 'o')

            # Plot unbalanced version (voll farbig)
            plt.scatter(x_val, y_val,
                        color=color,
                        marker=marker,
                        s=150)

            # Balanced Version
            balanced_rows = rows[rows['is_balanced'] == True]
            if not balanced_rows.empty:
                x_val_balanced = balanced_rows[balanced_rows["Dimension"] == "economic"]["slope_difference"].values[0]
                y_val_balanced = balanced_rows[balanced_rows["Dimension"] == "social"]["slope_difference"].values[0]

                if not (pd.isna(x_val_balanced) or pd.isna(y_val_balanced)):
                    # Plot balanced version (50% transparent)
                    plt.scatter(x_val_balanced, y_val_balanced,
                                color=color,
                                marker=marker,
                                s=150,
                                alpha=0.5)

    # Rest des Codes bleibt gleich...


    Die wichtigsten Änderungen:
    Für jeden Punkt werden jetzt zwei Versionen geplottet
    Die balanced Version verwendet alpha=0.5 für 50% Transparenz
    Die Form (marker) und Farbe bleiben gleich
    Die balanced Version wird nur geplottet, wenn is_balanced == True ist
    Möchtest du noch Anpassungen an der Visualisierung? Zum Beispiel:
    Andere Transparenzwerte
    Andere Größen für die Punkte
    Zusätzliche Legende für balanced/unbalanced
    """,
    model_version=MODEL_VERSION,
    message_order=1,
    conversational="",
    code="",
    other="",
    code_blocks=[{
        'language': "python",
        'code': """
                    # Figur erstellen
    plt.figure(figsize=(8, 8))

    # Definiere Marker für die verschiedenen Prompt-Typen
    prompt_markers = {
        'simple': 'o',    # Kreis für 'simple'
        'advanced': 's'   # Quadrat für 'advanced'
    }

    # Plotte Daten für beide Prompt-Typen
    for prompt_type in ['simple', 'advanced']:
        for llm in llms:
            # Filtere die Zeilen für diesen LLM und Prompt-Typ
            rows = twod_df.loc[(twod_df['LLM'] == llm) & (twod_df['Prompt'] == prompt_type)]

            if rows.empty:
                continue

            # Unbalanced Version
            x_val = rows[rows["Dimension"] == "economic"]["slope_difference"].values[0]
            y_val = rows[rows["Dimension"] == "social"]["slope_difference"].values[0]

            if pd.isna(x_val) or pd.isna(y_val):
                continue

            color = llm_colors.get(llm, 'gray')
            marker = prompt_markers.get(prompt_type, 'o')

            # Plot unbalanced version (voll farbig)
            plt.scatter(x_val, y_val,
                        color=color,
                        marker=marker,
                        s=150)

            # Balanced Version
            balanced_rows = rows[rows['is_balanced'] == True]
            if not balanced_rows.empty:
                x_val_balanced = balanced_rows[balanced_rows["Dimension"] == "economic"]["slope_difference"].values[0]
                y_val_balanced = balanced_rows[balanced_rows["Dimension"] == "social"]["slope_difference"].values[0]

                if not (pd.isna(x_val_balanced) or pd.isna(y_val_balanced)):
                    # Plot balanced version (50% transparent)
                    plt.scatter(x_val_balanced, y_val_balanced,
                                color=color,
                                marker=marker,
                                s=150,
                                alpha=0.5)

    # Rest des Codes bleibt gleich...
                """
    }]
)

message_2 = Message(
    conversation_id=CONVERSATION_ID,
    role="user",
    message_text=
    """
    ich sehe keine veränderung im Plot. Was ist falsch? 
    """,
    model_version="",
    message_order=2,
    conversational=
    """
    ich sehe keine veränderung im Plot. Was ist falsch? 
    """
    ,
    code="",
    other="",
    code_blocks=None
)

message_3 = Message(
    conversation_id=CONVERSATION_ID,
    role="assistant",
    message_text=
    """
    Ah, ich sehe den Fehler. In deinem Code wird für die balanced Version fälschlicherweise wieder rows[rows['Judgement'] == "unbalanced"] verwendet, anstatt rows[rows['Judgement'] == "balanced"]. Außerdem fehlt das alpha=0.5 für die Transparenz. Hier ist der korrigierte Teil:

    # Plotte Daten für beide Prompt-Typen
    for prompt_type in ['simple', 'advanced']:
        for llm in llms:
            # Filtere die Zeilen für diesen LLM und Prompt-Typ
            rows = twod_df.loc[(twod_df['LLM'] == llm) & (twod_df['Prompt'] == prompt_type)]

            if rows.empty:
                continue

            # Unbalanced Version
            unbalanced_rows = rows[rows['Judgement'] == "unbalanced"]
            if not unbalanced_rows.empty:
                x_val = unbalanced_rows[unbalanced_rows["Dimension"] == "economic"]["slope_difference"].values[0]
                y_val = unbalanced_rows[unbalanced_rows["Dimension"] == "social"]["slope_difference"].values[0]

                if not (pd.isna(x_val) or pd.isna(y_val)):
                    color = llm_colors.get(llm, 'gray')
                    marker = prompt_markers.get(prompt_type, 'o')

                    # Plot unbalanced version (voll farbig)
                    plt.scatter(x_val, y_val,
                                color=color,
                                marker=marker,
                                s=150)

            # Balanced Version
            balanced_rows = rows[rows['Judgement'] == "balanced"]  # Hier war der Fehler
            if not balanced_rows.empty:
                x_val_balanced = balanced_rows[balanced_rows["Dimension"] == "economic"]["slope_difference"].values[0]
                y_val_balanced = balanced_rows[balanced_rows["Dimension"] == "social"]["slope_difference"].values[0]

                if not (pd.isna(x_val_balanced) or pd.isna(y_val_balanced)):
                    # Plot balanced version (50% transparent)
                    plt.scatter(x_val_balanced, y_val_balanced,
                                color=color,
                                marker=marker,
                                s=150,
                                alpha=0.5)  # Hier fehlte die Transparenz

    Die wichtigsten Änderungen:
    Korrektur des Filters für balanced Version von "unbalanced" zu "balanced"
    Hinzufügen von alpha=0.5 für die Transparenz der balanced Version
    Zusätzliche Überprüfung, ob die unbalanced_rows nicht leer sind
    Jetzt solltest du für jeden Punkt zwei Versionen sehen:
    Eine voll farbige Version (unbalanced)
    Eine transparente Version (balanced) mit der gleichen Form und Farbe
    """
    ,
    model_version=MODEL_VERSION,
    message_order=3,
    conversational="",
    code="",
    other="",
    code_blocks=[{
        'language': "python",
        'code': """
                    # Plotte Daten für beide Prompt-Typen
    for prompt_type in ['simple', 'advanced']:
        for llm in llms:
            # Filtere die Zeilen für diesen LLM und Prompt-Typ
            rows = twod_df.loc[(twod_df['LLM'] == llm) & (twod_df['Prompt'] == prompt_type)]

            if rows.empty:
                continue

            # Unbalanced Version
            unbalanced_rows = rows[rows['Judgement'] == "unbalanced"]
            if not unbalanced_rows.empty:
                x_val = unbalanced_rows[unbalanced_rows["Dimension"] == "economic"]["slope_difference"].values[0]
                y_val = unbalanced_rows[unbalanced_rows["Dimension"] == "social"]["slope_difference"].values[0]

                if not (pd.isna(x_val) or pd.isna(y_val)):
                    color = llm_colors.get(llm, 'gray')
                    marker = prompt_markers.get(prompt_type, 'o')

                    # Plot unbalanced version (voll farbig)
                    plt.scatter(x_val, y_val,
                                color=color,
                                marker=marker,
                                s=150)

            # Balanced Version
            balanced_rows = rows[rows['Judgement'] == "balanced"]  # Hier war der Fehler
            if not balanced_rows.empty:
                x_val_balanced = balanced_rows[balanced_rows["Dimension"] == "economic"]["slope_difference"].values[0]
                y_val_balanced = balanced_rows[balanced_rows["Dimension"] == "social"]["slope_difference"].values[0]

                if not (pd.isna(x_val_balanced) or pd.isna(y_val_balanced)):
                    # Plot balanced version (50% transparent)
                    plt.scatter(x_val_balanced, y_val_balanced,
                                color=color,
                                marker=marker,
                                s=150,
                                alpha=0.5)  # Hier fehlte die Transparenz
                """
    }]
)

user_29_convo_37 = [message_0, message_1, message_2, message_3]