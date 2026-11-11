_slice_completions() {
    local cur prev commands instances
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    commands="create list ls stats top invite gpu port key backup exec enter root start stop restart delete rm"

    if [ $COMP_CWORD -eq 1 ]; then
        COMPREPLY=( $(compgen -W "$commands" -- "$cur") )
        return 0
    fi

    case "$prev" in
        invite|enter|root|start|stop|restart|delete|rm|exec|backup)
            instances=$(sudo incus list -c n --format csv 2>/dev/null | grep "^slice-" | sed "s/^slice-//" || true)
            COMPREPLY=( $(compgen -W "$instances" -- "$cur") )
            return 0
            ;;
        gpu)
            COMPREPLY=( $(compgen -W "attach detach" -- "$cur") )
            return 0
            ;;
        port)
            COMPREPLY=( $(compgen -W "add list" -- "$cur") )
            return 0
            ;;
        key)
            COMPREPLY=( $(compgen -W "add list clear" -- "$cur") )
            return 0
            ;;
    esac
}
complete -F _slice_completions slice
