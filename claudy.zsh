#!/usr/bin/env zsh
# Claudy zsh widget setup
# Usage: Type a partial command and press Ctrl-G to get a streaming suggestion

claudy-widget() {
    emulate -L zsh
    setopt local_options no_xtrace no_verbose no_monitor

    [[ -z "$BUFFER" ]] && return

    local original_buffer="$BUFFER"
    local original_cursor=$CURSOR

    local -a spinner=('⠋' '⠙' '⠹' '⠸' '⠼' '⠴' '⠦' '⠧' '⠇' '⠏')
    local spin_idx=0

    # Find claudy.py script
    local script_path=""
    if [[ -n "$CLAUDY_PATH" ]]; then
        # Use user-specified path
        script_path="$CLAUDY_PATH"
    elif [[ -f "${0:A:h}/claudy.py" ]]; then
        # Look in same directory as this file
        script_path="${0:A:h}/claudy.py"
    elif command -v claudy.py &>/dev/null; then
        # Look in PATH
        script_path=$(command -v claudy.py)
    elif [[ -f "$HOME/code/claudy/claudy.py" ]]; then
        # Look in ~/code/claudy
        script_path="$HOME/code/claudy/claudy.py"
    else
        echo "Error: Cannot find claudy.py" >&2
        return 1
    fi

    local tmpfile=$(mktemp)

    # Start background process in subshell
    ( "$script_path" "$original_buffer" > "$tmpfile" 2>/dev/null ) &
    local pid=$!

    local suggestion=""
    local first_token=1
    local last_size=0

    # Show spinner and poll for streaming output
    while kill -0 $pid 2>/dev/null; do
        if [[ -f "$tmpfile" ]]; then
            local current_size=$(stat -f%z "$tmpfile" 2>/dev/null || echo 0)

            if [[ $current_size -gt 0 ]]; then
                suggestion=$(cat "$tmpfile" 2>/dev/null)

                if [[ -n "$suggestion" && $current_size -ne $last_size ]]; then
                    # Got new content
                    if [[ $first_token -eq 1 ]]; then
                        # First token - clear the natural language
                        first_token=0
                    fi
                    BUFFER="$suggestion"
                    CURSOR=${#BUFFER}
                    zle -R
                    last_size=$current_size
                fi
                sleep 0.03
            else
                # Still waiting for first output - show spinner
                BUFFER="${original_buffer} ${spinner[$(( (spin_idx % 10) + 1 ))]}"
                zle -R
                spin_idx=$((spin_idx + 1))
                sleep 0.08
            fi
        else
            # File doesn't exist yet - show spinner
            BUFFER="${original_buffer} ${spinner[$(( (spin_idx % 10) + 1 ))]}"
            zle -R
            spin_idx=$((spin_idx + 1))
            sleep 0.08
        fi
    done

    # Wait for process to complete
    wait $pid 2>/dev/null

    # Get final output
    suggestion=$(cat "$tmpfile" 2>/dev/null)
    rm -f "$tmpfile"

    # Use suggestion or restore original
    if [[ -n "$suggestion" ]]; then
        BUFFER="$suggestion"
        CURSOR=${#BUFFER}
    else
        BUFFER="$original_buffer"
        CURSOR=$original_cursor
    fi

    zle -R
}

zle -N claudy-widget
bindkey '^G' claudy-widget
